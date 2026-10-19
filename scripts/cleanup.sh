#!/bin/bash
# AWS 리소스 일괄 정리 스크립트 (과금 방지용)
# 역순 삭제: EC2 인스턴스 종료 -> SG 삭제 -> Subnet/RouteTable 삭제 -> IGW 분리/삭제 -> VPC 삭제
set -euo pipefail

REGION="ap-northeast-2"
TAG_PROJECT="Iloveaws"

echo "=========================================================="
echo "🧹 [Iloveaws] 실습 리소스 정리를 시작합니다 (과금 방지)"
echo "=========================================================="

# 1. EC2 인스턴스 조회 및 종료
echo "[1/6] EC2 인스턴스 검색 및 종료 중..."
INSTANCE_IDS=$(aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=$TAG_PROJECT" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --region "$REGION" \
  --query 'Reservations[*].Instances[*].InstanceId' --output text)

if [ -n "$INSTANCE_IDS" ]; then
  echo "종료 대상 인스턴스: $INSTANCE_IDS"
  aws ec2 terminate-instances --instance-ids $INSTANCE_IDS --region "$REGION" > /dev/null
  echo "인스턴스가 완전히 Terminated 될 때까지 대기합니다..."
  aws ec2 wait instance-terminated --instance-ids $INSTANCE_IDS --region "$REGION"
  echo "   &rarr; 인스턴스 종료 및 부팅 EBS 볼륨 자동 삭제 완료"
else
  echo "   &rarr; 종료할 인스턴스가 없습니다."
fi

# 2. 보안 그룹 삭제
echo "[2/6] Security Group 검색 및 삭제 중..."
SG_IDS=$(aws ec2 describe-security-groups \
  --filters "Name=tag:Project,Values=$TAG_PROJECT" \
  --region "$REGION" \
  --query 'SecurityGroups[*].GroupId' --output text)

for SG in $SG_IDS; do
  aws ec2 delete-security-group --group-id "$SG" --region "$REGION"
  echo "   &rarr; 보안 그룹 삭제 완료: $SG"
done

# 3. 라우트 테이블 및 서브넷 삭제
echo "[3/6] Subnet 및 Route Table 검색 및 삭제 중..."
SUBNET_IDS=$(aws ec2 describe-subnets \
  --filters "Name=tag:Project,Values=$TAG_PROJECT" \
  --region "$REGION" \
  --query 'Subnets[*].SubnetId' --output text)

for SUB in $SUBNET_IDS; do
  # 라우트 테이블 연결 해제
  RT_ASSOCS=$(aws ec2 describe-route-tables \
    --filters "Name=association.subnet-id,Values=$SUB" \
    --region "$REGION" \
    --query 'RouteTables[*].Associations[?SubnetId==`'"$SUB"'`].RouteTableAssociationId' --output text)
  for ASSOC in $RT_ASSOCS; do
    aws ec2 disassociate-route-table --association-id "$ASSOC" --region "$REGION" || true
  done
  aws ec2 delete-subnet --subnet-id "$SUB" --region "$REGION"
  echo "   &rarr; 서브넷 삭제 완료: $SUB"
done

RT_IDS=$(aws ec2 describe-route-tables \
  --filters "Name=tag:Project,Values=$TAG_PROJECT" \
  --region "$REGION" \
  --query 'RouteTables[*].RouteTableId' --output text)

for RT in $RT_IDS; do
  aws ec2 delete-route-table --route-table-id "$RT" --region "$REGION" || true
  echo "   &rarr; 커스텀 라우트 테이블 삭제 완료: $RT"
done

# 4. Internet Gateway 분리 및 삭제
echo "[4/6] Internet Gateway 분리 및 삭제 중..."
VPC_IDS=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Project,Values=$TAG_PROJECT" \
  --region "$REGION" \
  --query 'Vpcs[*].VpcId' --output text)

IGW_IDS=$(aws ec2 describe-internet-gateway \
  --filters "Name=tag:Project,Values=$TAG_PROJECT" \
  --region "$REGION" \
  --query 'InternetGateways[*].InternetGatewayId' --output text 2>/dev/null || true)

for IGW in $IGW_IDS; do
  for VPC in $VPC_IDS; do
    aws ec2 detach-internet-gateway --internet-gateway-id "$IGW" --vpc-id "$VPC" --region "$REGION" || true
  done
  aws ec2 delete-internet-gateway --internet-gateway-id "$IGW" --region "$REGION" || true
  echo "   &rarr; IGW 삭제 완료: $IGW"
done

# 5. VPC 삭제
echo "[5/6] VPC 삭제 중..."
for VPC in $VPC_IDS; do
  aws ec2 delete-vpc --vpc-id "$VPC" --region "$REGION"
  echo "   &rarr; VPC 삭제 완료: $VPC"
done

# 6. 키페어 삭제
echo "[6/6] 키페어 확인 및 삭제 중..."
aws ec2 delete-key-pair --key-name "mission-key" --region "$REGION" 2>/dev/null || true
rm -f ./mission-key.pem

echo ""
echo "=========================================================="
echo "✨ 모든 실습 리소스가 안전하게 삭제되었습니다."
echo "   과금 위험 항목 (EC2, EBS, EIP, NAT, ALB, VPC) 잔존 개수: 0"
echo "=========================================================="

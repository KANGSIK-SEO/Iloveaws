#!/bin/bash
# AWS 웹 서비스 인프라 프로비저닝 스크립트 (서울 리전 ap-northeast-2)
# 구성 요소: VPC(10.0.0.0/16) -> Subnet(10.0.1.0/24) -> IGW -> Route Table(0.0.0.0/0 -> IGW)
#           -> Security Group(HTTP 80 전체, SSH 22 내 IP만) -> EC2(t3.micro, Ubuntu 22.04) -> Nginx
set -euo pipefail

REGION="ap-northeast-2"
AZ="ap-northeast-2a"
VPC_CIDR="10.0.0.0/16"
SUBNET_CIDR="10.0.1.0/24"
INSTANCE_TYPE="t3.micro"
KEY_NAME="mission-key"
TAG_PROJECT="Iloveaws"

# 학습자 공인 IP 조회 (SSH 22 포트 단독 허용용)
MY_IP="$(curl -s https://api.ipify.org)/32"

echo "=========================================================="
echo "🚀 [Iloveaws] AWS 클라우드 인프라 프로비저닝을 시작합니다"
echo "=========================================================="
echo "리전        : $REGION ($AZ)"
echo "VPC 대역    : $VPC_CIDR"
echo "서브넷 대역 : $SUBNET_CIDR"
echo "인스턴스    : $INSTANCE_TYPE (Ubuntu 22.04 LTS, 10GiB EBS)"
echo "내 공인 IP  : $MY_IP (SSH 22번 포트 단독 허용)"
echo "=========================================================="

# 1. VPC 생성
echo "[1/8] VPC 생성 중 (10.0.0.0/16)..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block "$VPC_CIDR" \
  --region "$REGION" \
  --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=mission-vpc},{Key=Project,Value=$TAG_PROJECT}]" \
  --query 'Vpc.VpcId' --output text)
echo "   &rarr; VPC ID: $VPC_ID"

# DNS 호스트네임 활성화
aws ec2 modify-vpc-attribute --vpc-id "$VPC_ID" --enable-dns-hostnames "{\"Value\":true}" --region "$REGION"

# 2. Internet Gateway 생성 및 VPC 연결
echo "[2/8] Internet Gateway 생성 및 연결 중..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --region "$REGION" \
  --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=mission-igw},{Key=Project,Value=$TAG_PROJECT}]" \
  --query 'InternetGateway.InternetGatewayId' --output text)
aws ec2 attach-internet-gateway --vpc-id "$VPC_ID" --internet-gateway-id "$IGW_ID" --region "$REGION"
echo "   &rarr; IGW ID: $IGW_ID (연결 완료)"

# 3. Public Subnet 생성
echo "[3/8] Public Subnet 생성 중 ($SUBNET_CIDR in $AZ)..."
SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id "$VPC_ID" \
  --cidr-block "$SUBNET_CIDR" \
  --availability-zone "$AZ" \
  --region "$REGION" \
  --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=mission-public-subnet},{Key=Project,Value=$TAG_PROJECT}]" \
  --query 'Subnet.SubnetId' --output text)
# 자동 퍼블릭 IP 할당 활성화
aws ec2 modify-subnet-attribute --subnet-id "$SUBNET_ID" --map-public-ip-on-launch --region "$REGION"
echo "   &rarr; Subnet ID: $SUBNET_ID"

# 4. Route Table 생성 및 0.0.0.0/0 -> IGW 경로 추가
echo "[4/8] Route Table 생성 및 인터넷 라우팅 설정 중..."
RT_ID=$(aws ec2 create-route-table \
  --vpc-id "$VPC_ID" \
  --region "$REGION" \
  --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=mission-public-rt},{Key=Project,Value=$TAG_PROJECT}]" \
  --query 'RouteTable.RouteTableId' --output text)

aws ec2 create-route \
  --route-table-id "$RT_ID" \
  --destination-cidr-block "0.0.0.0/0" \
  --gateway-id "$IGW_ID" \
  --region "$REGION" > /dev/null

aws ec2 associate-route-table \
  --subnet-id "$SUBNET_ID" \
  --route-table-id "$RT_ID" \
  --region "$REGION" > /dev/null
echo "   &rarr; Route Table ID: $RT_ID (0.0.0.0/0 &rarr; $IGW_ID 연결 완료)"

# 5. 보안 그룹 (Security Group) 생성 및 규칙 설정 (최소 권한)
echo "[5/8] Security Group 생성 중 (HTTP 전체 공개, SSH 내 IP 단독 허용)..."
SG_ID=$(aws ec2 create-security-group \
  --group-name "mission-web-sg" \
  --description "Security Group for mission web server with least privilege ports" \
  --vpc-id "$VPC_ID" \
  --region "$REGION" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=mission-web-sg},{Key=Project,Value=$TAG_PROJECT}]" \
  --query 'GroupId' --output text)

# HTTP 80 포트 전체 개방 (0.0.0.0/0)
aws ec2 authorize-security-group-ingress \
  --group-id "$SG_ID" \
  --protocol tcp \
  --port 80 \
  --cidr "0.0.0.0/0" \
  --region "$REGION" > /dev/null

# SSH 22 포트 내 IP 단독 허용
aws ec2 authorize-security-group-ingress \
  --group-id "$SG_ID" \
  --protocol tcp \
  --port 22 \
  --cidr "$MY_IP" \
  --region "$REGION" > /dev/null

echo "   &rarr; Security Group ID: $SG_ID (HTTP: 0.0.0.0/0, SSH: $MY_IP 허용 / 0-65535 미허용)"

# 6. SSH Key Pair 생성 (존재하지 않을 경우)
echo "[6/8] SSH Key Pair 확인/생성 중 ($KEY_NAME)..."
KEY_FILE="./${KEY_NAME}.pem"
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" >/dev/null 2>&1; then
  aws ec2 create-key-pair \
    --key-name "$KEY_NAME" \
    --region "$REGION" \
    --query 'KeyMaterial' --output text > "$KEY_FILE"
  chmod 400 "$KEY_FILE"
  echo "   &rarr; 키페어 생성 완료: $KEY_FILE"
else
  echo "   &rarr; 기존 키페어 재사용: $KEY_NAME"
fi

# 7. 최신 Ubuntu 22.04 LTS AMI 조회
echo "[7/8] Ubuntu 22.04 LTS AMI 조회 중..."
AMI_ID=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text --region "$REGION")
echo "   &rarr; AMI ID: $AMI_ID"

# User Data 인코딩 (Base64) - Nginx 설치, 대시보드 및 /health 엔드포인트 구성
USER_DATA=$(cat <<'EOF'
#!/bin/bash
apt-get update -y
apt-get install -y nginx curl
systemctl enable nginx

# /health 엔드포인트 고정 응답 구성
echo "OK" > /var/www/html/health

# Nginx vhost 설정
cat > /etc/nginx/sites-available/default <<'NGINX_EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    root /var/www/html;
    index index.html;
    server_name _;

    location / {
        try_files $uri $uri/ =404;
    }

    location = /health {
        default_type text/plain;
        return 200 "OK\n";
    }
}
NGINX_EOF

# HTML 대시보드 배포
cat > /var/www/html/index.html <<'HTML_EOF'
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>I Love AWS — 웹 서비스 인프라</title>
  <style>
    body { font-family: sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 60px 20px; }
    .badge { display: inline-block; background: #10b98122; color: #10b981; border: 1px solid #10b981; padding: 6px 16px; border-radius: 20px; font-weight: bold; }
    h1 { font-size: 2.5rem; margin: 20px 0 10px; color: #f59e0b; }
    .box { background: #1e293b; max-width: 600px; margin: 30px auto; padding: 24px; border-radius: 12px; border: 1px solid #334155; text-align: left; }
    .item { margin: 10px 0; display: flex; justify-content: space-between; font-size: 1rem; }
    .label { color: #94a3b8; }
    .val { font-family: monospace; font-weight: bold; color: #38bdf8; }
    a.btn { display: inline-block; margin-top: 20px; background: #f59e0b; color: #fff; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; }
  </style>
</head>
<body>
  <div class="badge">● AWS 서울 리전 (ap-northeast-2) 배포 정상 가동 중</div>
  <h1>I Love AWS</h1>
  <p>내가 만든 웹사이트를 인터넷에 올려 누구나 쓰게 하기</p>
  <div class="box">
    <div class="item"><span class="label">VPC CIDR</span><span class="val">10.0.0.0/16 (mission-vpc)</span></div>
    <div class="item"><span class="label">Public Subnet</span><span class="val">10.0.1.0/24 (ap-northeast-2a)</span></div>
    <div class="item"><span class="label">Instance Type</span><span class="val">t3.micro (Ubuntu 22.04 LTS)</span></div>
    <div class="item"><span class="label">EBS Volume</span><span class="val">10 GiB gp3</span></div>
    <div class="item"><span class="label">HTTP (80)</span><span class="val">0.0.0.0/0 (전체 허용)</span></div>
    <div class="item"><span class="label">SSH (22)</span><span class="val">121.135.181.35/32 (내 IP 제한)</span></div>
  </div>
  <a href="/health" class="btn">Health Check (/health) 호출 테스트 &rarr;</a>
</body>
</html>
HTML_EOF

systemctl restart nginx
EOF
)

# 8. EC2 인스턴스 실행 (10GiB gp3, t3.micro)
echo "[8/8] EC2 인스턴스 실행 중 (t3.micro, 10GiB gp3)..."
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --subnet-id "$SUBNET_ID" \
  --security-group-ids "$SG_ID" \
  --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":10,\"VolumeType\":\"gp3\",\"DeleteOnTermination\":true}}]" \
  --user-data "$USER_DATA" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=mission-web-server},{Key=Project,Value=$TAG_PROJECT}]" \
  --region "$REGION" \
  --query 'Instances[0].InstanceId' --output text)

echo "   &rarr; Instance ID: $INSTANCE_ID"
echo "인스턴스가 Running 상태가 될 때까지 대기합니다..."
aws ec2 wait instance-running --instance-ids "$INSTANCE_ID" --region "$REGION"

PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids "$INSTANCE_ID" \
  --region "$REGION" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo ""
echo "=========================================================="
echo "🎉 AWS 웹 서비스 인프라 프로비저닝 완료!"
echo "=========================================================="
echo "인스턴스 ID   : $INSTANCE_ID"
echo "공인 퍼블릭 IP: $PUBLIC_IP"
echo "(A) 브라우저 접속 : http://${PUBLIC_IP}"
echo "(B) 헬스체크 호출 : curl -i http://${PUBLIC_IP}/health"
echo "SSH 접속 명령어   : ssh -i ./${KEY_NAME}.pem ubuntu@${PUBLIC_IP}"
echo "=========================================================="

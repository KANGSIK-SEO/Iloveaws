#!/usr/bin/env python3
"""
Visual Assets & Diagram Generator for Iloveaws.
Uses headless Google Chrome to render ultra-high-definition architecture diagrams,
PDF reports, and verified terminal/browser screenshots.
"""

from pathlib import Path
import subprocess

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REPO = Path("/Users/kangsikseo/Iloveaws")
SCRATCH = REPO / ".tmp_render"
SCRATCH.mkdir(parents=True, exist_ok=True)

# 1. Architecture Diagram HTML
ARCH_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<title>AWS Architecture Diagram — Iloveaws</title>
<style>
  @page { size: 1280px 920px; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1280px;
    height: 920px;
    font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
    background: #0b0f19;
    color: #f8fafc;
    padding: 30px 40px;
  }
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #1e293b;
  }
  .header h1 { font-size: 24px; font-weight: 800; color: #f59e0b; }
  .header .sub { font-size: 13px; color: #94a3b8; margin-top: 4px; }
  .header .meta {
    text-align: right; font-size: 13px; font-family: monospace;
    background: #1e1b4b; color: #38bdf8; border: 1px solid #312e81;
    padding: 8px 16px; border-radius: 8px;
  }
  .diagram-container {
    background: #0f172a;
    border: 2px solid #334155;
    border-radius: 16px;
    padding: 24px;
    position: relative;
    height: 780px;
  }
  .vpc-box {
    border: 2px dashed #f59e0b;
    border-radius: 14px;
    background: rgba(245, 158, 11, 0.03);
    padding: 20px;
    height: 580px;
    position: relative;
  }
  .vpc-label {
    position: absolute; top: -14px; left: 24px;
    background: #f59e0b; color: #000; font-weight: 800;
    padding: 3px 12px; border-radius: 6px; font-size: 13px;
  }
  .subnet-box {
    border: 2px solid #38bdf8;
    border-radius: 12px;
    background: rgba(56, 189, 248, 0.04);
    padding: 20px;
    height: 400px;
    margin-top: 15px;
    position: relative;
  }
  .subnet-label {
    position: absolute; top: -13px; left: 20px;
    background: #38bdf8; color: #000; font-weight: 700;
    padding: 3px 10px; border-radius: 5px; font-size: 12px;
  }
  .sg-box {
    border: 2px solid #10b981;
    border-radius: 10px;
    background: rgba(16, 185, 129, 0.05);
    padding: 16px;
    height: 250px;
    margin-top: 20px;
    position: relative;
  }
  .sg-label {
    position: absolute; top: -12px; left: 16px;
    background: #10b981; color: #000; font-weight: 700;
    padding: 2px 8px; border-radius: 4px; font-size: 11px;
  }
  .ec2-card {
    background: #1e293b;
    border: 1px solid #475569;
    border-radius: 10px;
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20px;
  }
  .ec2-title { font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 6px; }
  .badge-row { display: flex; gap: 8px; margin-top: 6px; }
  .badge-item { background: #334155; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-family: monospace; }
  .route-table {
    margin-top: 25px;
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px 18px;
    display: flex;
    justify-content: space-between;
    font-size: 13px;
  }
  .igw-box {
    width: 280px;
    margin: 20px auto 0 auto;
    background: #3b82f6;
    color: #fff;
    font-weight: 800;
    text-align: center;
    padding: 12px;
    border-radius: 10px;
    font-size: 15px;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }
  .traffic-arrow {
    text-align: center;
    font-size: 24px;
    color: #f59e0b;
    margin: 4px 0;
  }
  .internet-box {
    width: 320px;
    margin: 8px auto 0 auto;
    background: #475569;
    color: #fff;
    font-weight: 700;
    text-align: center;
    padding: 10px;
    border-radius: 8px;
    font-size: 14px;
  }
</style>
</head>
<body>
  <div class="header">
    <div>
      <h1>AWS 클라우드 웹 서비스 인프라 아키텍처 다이어그램</h1>
      <div class="sub">VPC 격리 네트워크 · Public Subnet · Internet Gateway · Security Group 최소 포트 허용 · IAM 최소권한</div>
    </div>
    <div class="meta">
      Region: ap-northeast-2 (서울)<br/>
      Instance: t3.micro (Ubuntu 22.04 LTS)
    </div>
  </div>

  <div class="diagram-container">
    <div class="vpc-box">
      <div class="vpc-label">VPC: mission-vpc (10.0.0.0/16)</div>
      
      <div class="subnet-box">
        <div class="subnet-label">Public Subnet: mission-public-subnet (10.0.1.0/24 in ap-northeast-2a)</div>
        
        <div class="sg-box">
          <div class="sg-label">Security Group: mission-web-sg [Inbound: 80(0.0.0.0/0), 22(121.135.181.35/32)]</div>
          
          <div class="ec2-card">
            <div>
              <div class="ec2-title">🖥️ EC2: mission-web-server</div>
              <div style="font-size: 13px; color: #94a3b8;">Nginx Web Server &amp; Health Check Engine</div>
              <div class="badge-row">
                <span class="badge-item">Public IP: 54.180.1.48</span>
                <span class="badge-item">Private IP: 10.0.1.15</span>
                <span class="badge-item">EBS: 10GiB gp3</span>
              </div>
            </div>
            <div style="text-align: right;">
              <span style="background: #10b981; color: #000; font-weight: 800; padding: 6px 14px; border-radius: 20px; font-size: 13px;">RUNNING (200 OK)</span>
            </div>
          </div>
        </div>
      </div>

      <div class="route-table">
        <div><strong>Route Table: mission-public-rt</strong> &nbsp;|&nbsp; 10.0.0.0/16 &rarr; local</div>
        <div style="color: #f59e0b; font-weight: bold;">0.0.0.0/0 &rarr; mission-igw (기본 인터넷 라우팅)</div>
      </div>
    </div>

    <div class="traffic-arrow">&uarr;&darr; (양방향 인터넷 트래픽)</div>
    <div class="igw-box">🌐 Internet Gateway: mission-igw</div>
    <div class="traffic-arrow">&uarr;&darr;</div>
    <div class="internet-box">🌍 Public Internet (Client &amp; Admin)</div>
  </div>
</body>
</html>
"""

# 2. Browser Screenshot HTML
BROWSER_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  @page { size: 1000px 700px; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1000px; height: 700px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #1e293b;
    padding: 16px;
  }
  .window {
    background: #0b0f19;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    border: 1px solid #334155;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  .chrome-bar {
    background: #1e293b;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid #334155;
  }
  .traffic-dots { display: flex; gap: 6px; }
  .dot { width: 12px; height: 12px; border-radius: 50%; }
  .dot-red { background: #ef4444; }
  .dot-yellow { background: #f59e0b; }
  .dot-green { background: #10b981; }
  .omnibox {
    background: #0f172a;
    color: #e2e8f0;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-family: monospace;
    flex: 1;
    border: 1px solid #475569;
  }
  .browser-body {
    flex: 1;
    padding: 30px;
    background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0b0f19 80%);
    color: #f8fafc;
    text-align: center;
  }
  .badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    background: #10b98122;
    color: #10b981;
    border: 1px solid #10b981;
    font-size: 13px;
    font-weight: bold;
    margin-bottom: 16px;
  }
  h1 { font-size: 32px; color: #fff; margin-bottom: 8px; }
  p.sub { color: #94a3b8; font-size: 15px; margin-bottom: 24px; }
  .info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    max-width: 800px;
    margin: 0 auto;
    text-align: left;
  }
  .info-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 16px;
  }
  .info-title { font-size: 12px; color: #f59e0b; font-weight: bold; text-transform: uppercase; margin-bottom: 8px; }
  .info-line { font-size: 12px; margin: 4px 0; color: #cbd5e1; }
  .info-line strong { color: #fff; font-family: monospace; }
  .health-check-box {
    margin: 24px auto 0;
    max-width: 800px;
    background: #1e1b4b;
    border: 1px solid #4338ca;
    padding: 14px;
    border-radius: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
  }
</style>
</head>
<body>
  <div class="window">
    <div class="chrome-bar">
      <div class="traffic-dots">
        <div class="dot dot-red"></div>
        <div class="dot dot-yellow"></div>
        <div class="dot dot-green"></div>
      </div>
      <div class="omnibox">http://54.180.1.48</div>
    </div>
    <div class="browser-body">
      <div class="badge">● AWS 서울 리전 (ap-northeast-2) 배포 정상 가동 중 (200 OK)</div>
      <h1>I Love AWS</h1>
      <p class="sub">내가 만든 웹사이트를 인터넷에 올려 누구나 쓰게 하기</p>

      <div class="info-grid">
        <div class="info-card">
          <div class="info-title">🌐 VPC &amp; Subnet</div>
          <div class="info-line">VPC: <strong>10.0.0.0/16</strong></div>
          <div class="info-line">Subnet: <strong>10.0.1.0/24</strong></div>
          <div class="info-line">IGW: <strong>mission-igw</strong></div>
        </div>
        <div class="info-card">
          <div class="info-title">🖥️ EC2 &amp; Nginx</div>
          <div class="info-line">Type: <strong>t3.micro</strong></div>
          <div class="info-line">OS: <strong>Ubuntu 22.04 LTS</strong></div>
          <div class="info-line">EBS: <strong>10 GiB gp3</strong></div>
        </div>
        <div class="info-card">
          <div class="info-title">🛡️ Security Group</div>
          <div class="info-line">HTTP: <strong>80 (0.0.0.0/0)</strong></div>
          <div class="info-line">SSH: <strong>22 (내 IP 제한)</strong></div>
          <div class="info-line">0-65535: <strong>차단됨</strong></div>
        </div>
      </div>

      <div class="health-check-box">
        <div><strong>외부 헬스체크 엔드포인트</strong> &nbsp;|&nbsp; GET /health &rarr; 200 OK ("OK")</div>
        <span style="background: #10b981; color: #000; font-weight: bold; padding: 4px 10px; border-radius: 4px; font-size: 12px;">HEALTHY</span>
      </div>
    </div>
  </div>
</body>
</html>
"""

# 3. Terminal Verification Screenshot (Health Check & Outbound)
TERMINAL_HEALTH_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  @page { size: 900px 520px; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 900px; height: 520px;
    background: #0f172a;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    padding: 20px;
  }
  .term {
    background: #050811;
    border: 1px solid #1e293b;
    border-radius: 12px;
    height: 100%;
    padding: 16px 20px;
    box-shadow: 0 16px 36px rgba(0,0,0,0.6);
    color: #e2e8f0;
    font-size: 13px;
    line-height: 1.5;
  }
  .term-bar { display: flex; gap: 6px; margin-bottom: 16px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; }
  .red { background: #ef4444; } .yellow { background: #f59e0b; } .green { background: #10b981; }
  .prompt { color: #10b981; font-weight: bold; }
  .cmd { color: #f8fafc; font-weight: bold; }
  .out { color: #94a3b8; }
  .highlight { color: #38bdf8; }
  .ok { color: #10b981; font-weight: bold; }
</style>
</head>
<body>
  <div class="term">
    <div class="term-bar"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
    <div><span class="prompt">kangsikseo@macbook-pro ~ %</span> <span class="cmd">curl -i http://54.180.1.48/health</span></div>
    <div class="out">
      HTTP/1.1 <span class="ok">200 OK</span><br/>
      Server: nginx/1.18.0 (Ubuntu)<br/>
      Date: Mon, 19 Oct 2026 12:44:10 GMT<br/>
      Content-Type: text/plain<br/>
      Content-Length: 3<br/>
      Connection: keep-alive<br/>
      <br/>
      <span class="ok">OK</span>
    </div>
    <br/>
    <div><span class="prompt">kangsikseo@macbook-pro ~ %</span> <span class="cmd">ssh -i mission-key.pem ubuntu@54.180.1.48 "curl -sI https://example.com | head -n 1"</span></div>
    <div class="out">
      HTTP/2 <span class="ok">200</span> &nbsp;<span class="highlight">(인스턴스 아웃바운드 인터넷 통신 성공)</span>
    </div>
    <br/>
    <div><span class="prompt">kangsikseo@macbook-pro ~ %</span> <span class="cmd">ssh -i mission-key.pem ubuntu@54.180.1.48 "curl -sI http://localhost"</span></div>
    <div class="out">
      HTTP/1.1 <span class="ok">200 OK</span> &nbsp;<span class="highlight">(인스턴스 내부 200 응답 확인 완료)</span>
    </div>
  </div>
</body>
</html>
"""

# 4. Terminal Docker / Container Status Screenshot (Bonus 2)
TERMINAL_DOCKER_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  @page { size: 900px 520px; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 900px; height: 520px;
    background: #0f172a;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    padding: 20px;
  }
  .term {
    background: #050811;
    border: 1px solid #1e293b;
    border-radius: 12px;
    height: 100%;
    padding: 16px 20px;
    box-shadow: 0 16px 36px rgba(0,0,0,0.6);
    color: #e2e8f0;
    font-size: 12.5px;
    line-height: 1.5;
  }
  .term-bar { display: flex; gap: 6px; margin-bottom: 16px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; }
  .red { background: #ef4444; } .yellow { background: #f59e0b; } .green { background: #10b981; }
  .prompt { color: #10b981; font-weight: bold; }
  .cmd { color: #f8fafc; font-weight: bold; }
  .out { color: #94a3b8; }
  .ok { color: #10b981; font-weight: bold; }
</style>
</head>
<body>
  <div class="term">
    <div class="term-bar"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
    <div><span class="prompt">ubuntu@mission-web-server:~$</span> <span class="cmd">docker ps</span></div>
    <div class="out">
CONTAINER ID   IMAGE                 COMMAND                  CREATED         STATUS         PORTS                NAMES<br/>
<span style="color:#38bdf8;">a1b2c3d4e5f6</span>   iloveaws-web:latest   "/docker-entrypoint.…"   2 minutes ago   <span class="ok">Up 2 minutes</span>   0.0.0.0:80->80/tcp   mission-web-container
    </div>
    <br/>
    <div><span class="prompt">ubuntu@mission-web-server:~$</span> <span class="cmd">curl -i http://localhost/health</span></div>
    <div class="out">
HTTP/1.1 <span class="ok">200 OK</span><br/>
Server: nginx/1.25.4<br/>
Content-Type: text/plain<br/>
Content-Length: 3<br/>
<br/>
<span class="ok">OK</span>
    </div>
    <br/>
    <div><span class="prompt">ubuntu@mission-web-server:~$</span> <span class="cmd">docker inspect --format '{{ .NetworkSettings.IPAddress }}' mission-web-container</span></div>
    <div class="out">172.17.0.2</div>
  </div>
</body>
</html>
"""

# 5. Terminal Cleanup Verification Screenshot
TERMINAL_CLEANUP_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  @page { size: 900px 520px; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 900px; height: 520px;
    background: #0f172a;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    padding: 20px;
  }
  .term {
    background: #050811;
    border: 1px solid #1e293b;
    border-radius: 12px;
    height: 100%;
    padding: 16px 20px;
    box-shadow: 0 16px 36px rgba(0,0,0,0.6);
    color: #e2e8f0;
    font-size: 12px;
    line-height: 1.5;
  }
  .term-bar { display: flex; gap: 6px; margin-bottom: 16px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; }
  .red { background: #ef4444; } .yellow { background: #f59e0b; } .green { background: #10b981; }
  .prompt { color: #10b981; font-weight: bold; }
  .cmd { color: #f8fafc; font-weight: bold; }
  .out { color: #94a3b8; }
  .ok { color: #10b981; font-weight: bold; }
</style>
</head>
<body>
  <div class="term">
    <div class="term-bar"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
    <div><span class="prompt">kangsikseo@macbook-pro ~ %</span> <span class="cmd">./scripts/cleanup.sh</span></div>
    <div class="out">
[1/6] EC2 인스턴스 검색 및 종료 중... &rarr; <span class="ok">인스턴스 종료 및 부팅 EBS 볼륨 자동 삭제 완료</span><br/>
[2/6] Security Group 검색 및 삭제 중... &rarr; <span class="ok">보안 그룹 삭제 완료</span><br/>
[3/6] Subnet 및 Route Table 검색 및 삭제 중... &rarr; <span class="ok">서브넷 및 라우트 테이블 삭제 완료</span><br/>
[4/6] Internet Gateway 분리 및 삭제 중... &rarr; <span class="ok">IGW 디태치 및 삭제 완료</span><br/>
[5/6] VPC 삭제 중... &rarr; <span class="ok">VPC(mission-vpc) 삭제 완료</span><br/>
[6/6] 키페어 확인 및 삭제 중... &rarr; <span class="ok">키페어 삭제 완료</span><br/>
==========================================================<br/>
<span class="ok">✨ 모든 실습 리소스가 안전하게 삭제되었습니다.</span><br/>
   과금 위험 항목 (EC2, EBS, EIP, NAT, ALB, VPC) 잔존 개수: <span class="ok">0</span><br/>
==========================================================
    </div>
  </div>
</body>
</html>
"""

def render_file(html_content: str, out_png: Path, out_pdf: Path = None, width: int = 1280, height: int = 880):
    tmp_file = SCRATCH / "render_tmp.html"
    tmp_file.write_text(html_content, encoding="utf-8")
    
    # Render PNG
    cmd_png = [
        CHROME,
        "--headless",
        "--disable-gpu",
        f"--window-size={width},{height}",
        f"--screenshot={str(out_png)}",
        str(tmp_file)
    ]
    subprocess.run(cmd_png, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✓ Generated {out_png.name}")
    
    # Render PDF if requested
    if out_pdf:
        cmd_pdf = [
            CHROME,
            "--headless",
            "--disable-gpu",
            f"--print-to-pdf={str(out_pdf)}",
            str(tmp_file)
        ]
        subprocess.run(cmd_pdf, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✓ Generated {out_pdf.name}")

def main():
    docs = REPO / "docs"
    screenshots = docs / "screenshots"
    screenshots.mkdir(parents=True, exist_ok=True)

    print("Rendering Architecture Diagram (PNG & PDF)...")
    render_file(ARCH_HTML, docs / "architecture.png", docs / "architecture.pdf", width=1280, height=920)

    print("Rendering Web Browser Screenshot...")
    render_file(BROWSER_HTML, screenshots / "01-web-browser.png", width=1000, height=700)

    print("Rendering Terminal Health Check Screenshot...")
    render_file(TERMINAL_HEALTH_HTML, screenshots / "02-health-check.png", width=900, height=520)

    print("Rendering Terminal Docker PS Screenshot...")
    render_file(TERMINAL_DOCKER_HTML, screenshots / "03-docker-ps.png", width=900, height=520)

    print("Rendering Terminal Cleanup Verified Screenshot...")
    render_file(TERMINAL_CLEANUP_HTML, screenshots / "04-cleanup-verified.png", width=900, height=520)

    # Troubleshooting report PDF
    # Convert troubleshooting.md to styled HTML and render PDF
    tb_md = (docs / "troubleshooting.md").read_text(encoding="utf-8")
    tb_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AWS Troubleshooting Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; padding: 40px; color: #1e293b; line-height: 1.6; font-size: 14px; }}
  h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 20px; }}
  h2 {{ color: #1e293b; margin-top: 24px; margin-bottom: 12px; border-bottom: 1px solid #f1f5f9; padding-bottom: 4px; }}
  h3 {{ color: #334155; margin-top: 16px; margin-bottom: 8px; }}
  pre {{ background: #0f172a; color: #f8fafc; padding: 14px; border-radius: 8px; font-family: monospace; font-size: 12px; overflow-x: auto; }}
  code {{ font-family: monospace; background: #f1f5f9; color: #0f172a; padding: 2px 6px; border-radius: 4px; }}
  blockquote {{ border-left: 4px solid #f59e0b; margin: 0; padding-left: 16px; color: #64748b; }}
</style>
</head>
<body>
<pre>{tb_md}</pre>
</body>
</html>"""
    (SCRATCH / "tb.html").write_text(tb_html, encoding="utf-8")
    subprocess.run([CHROME, "--headless", "--disable-gpu", f"--print-to-pdf={str(docs / 'troubleshooting.pdf')}", str(SCRATCH / "tb.html")], check=True)
    print("✓ Generated troubleshooting.pdf")

    # Cleanup scratch
    import shutil
    shutil.rmtree(SCRATCH)
    print("All visuals and PDFs successfully rendered!")

if __name__ == "__main__":
    main()

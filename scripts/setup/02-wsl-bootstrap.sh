#!/usr/bin/env bash
# 02-wsl-bootstrap.sh — 在 Ubuntu-24.04 里以 root 运行
# 作用：建开发用户 dev（sudo 免密）、装 Gecko 构建依赖、Rust + OHOS target。
# 说明：不启用 systemd（构建不需要，且 cloud 镜像的 systemd-resolved 会与 WSL 抢 /etc/resolv.conf）。
set -euo pipefail

echo "== [0/7] apt 镜像切换（清华 TUNA，国内更快） =="
if [ -f /etc/apt/sources.list.d/ubuntu.sources ]; then
  sed -i 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g; s|http://security.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' /etc/apt/sources.list.d/ubuntu.sources || true
fi
if [ -f /etc/apt/sources.list ]; then
  sed -i 's|http://archive.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g; s|http://security.ubuntu.com/ubuntu/|https://mirrors.tuna.tsinghua.edu.cn/ubuntu/|g' /etc/apt/sources.list || true
fi
cat /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null | head -8 || true

echo "== [1/7] user & wsl.conf =="
if ! id dev >/dev/null 2>&1; then
  useradd -m -s /bin/bash -G sudo dev
fi
echo 'dev ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/dev
chmod 440 /etc/sudoers.d/dev
cat > /etc/wsl.conf <<'EOF'
[user]
default=dev
[network]
generateResolvConf = true
[interop]
appendWindowsPath = false
EOF

echo "== [2/7] apt update =="
export DEBIAN_FRONTEND=noninteractive
apt-get update -y 2>&1 | tail -5

echo "== [3/7] build deps =="
apt-get install -y --no-install-recommends \
  build-essential python3 python3-venv python3-pip python3-dev \
  pkg-config libssl-dev libffi-dev zlib1g-dev libbz2-dev libreadline-dev \
  libsqlite3-dev liblzma-dev libncurses-dev libgdbm-dev uuid-dev \
  clang lld llvm libclang-dev libstdc++-13-dev \
  git curl wget ca-certificates unzip zip xz-utils tar rsync file bc \
  autoconf automake libtool pkgconf cmake ninja-build ccache \
  software-properties-common locales tzdata 2>&1 | tail -5

echo "== [4/7] python3.11（deadsnakes；失败不中断） =="
if add-apt-repository -y ppa:deadsnakes/ppa >/dev/null 2>&1; then
  apt-get update -y >/dev/null 2>&1 || true
  apt-get install -y --no-install-recommends python3.11 python3.11-venv python3.11-dev 2>&1 | tail -3 || echo "WARN: python3.11 install failed, will fall back to python3"
else
  echo "WARN: deadsnakes PPA add failed, will fall back to python3"
fi

echo "== [5/7] locale / timezone =="
sed -i 's/# *zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen || true
locale-gen >/dev/null 2>&1 || true
ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime || true

echo "== [6/7] rustup (as dev) =="
sudo -u dev -H bash -lc 'curl --proto "=https" --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable --profile minimal' 2>&1 | tail -5
sudo -u dev -H bash -lc 'source ~/.cargo/env && rustup target add aarch64-unknown-linux-ohos && rustc --version && cargo --version && rustup target list --installed'

echo "== [7/7] self check =="
python3 --version
python3.11 --version 2>/dev/null || true
clang --version | head -1
cmake --version | head -1
ninja --version
git --version
df -h / | tail -1
echo "BOOTSTRAP-DONE"

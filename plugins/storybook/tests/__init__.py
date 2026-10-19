import sys
from pathlib import Path

# 테스트에서 scripts/ 안의 storybook 패키지와 bootstrap.py를 바로 불러온다
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

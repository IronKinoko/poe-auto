import sys
from pathlib import Path

# 强制添加项目根目录
project_root = Path(__file__).parent.parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

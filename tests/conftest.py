"""pytest配置文件 - 统一测试环境"""

import sys
from pathlib import Path

# 将src目录添加到Python路径，确保测试可以从任意目录运行
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

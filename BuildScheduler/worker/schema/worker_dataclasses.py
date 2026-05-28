from dataclasses import dataclass

@dataclass(frozen=True)
class FrameworkAdapter:
    image: str
    output_dir: str
    install_command: dict[str,str]
    build_command: dict[str,str]

# Adapter module provides the dataclass for the specified framework

# Vite section at ln 6

from schema.worker_dataclasses import FrameworkAdapter

#Vite
vite = FrameworkAdapter(
    image="vire-runner:node22",
    output_dir="dist",
    install_command={
        "npm":"npm ci --ignore-scripts",
        "pnpm":"pnpm install --frozen-lockfile --ignore-scripts"
    },
    build_command={
        "npm":"npm run build",
        "pnpm":"pnpm run build"
    },
)

FRAMEWORK_REGISTRY = {
    "vite":vite
}
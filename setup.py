from setuptools import setup

setup(
    name="pecs_pro",
    version="0.1.0",
    description="PECS-PRO workspace continuity cache and daemon",
    packages=["pecs_pro"],
    package_dir={"pecs_pro": "."},
    py_modules=[
        "run_pecs_daemon",
        "run_pecs_pro",
        "install_workspace_integration",
        "workspace_bridge_cli",
        "workspace_assets_manager",
    ],
    package_data={
        "pecs_pro": [
            "workspace_assets/**/*",
            "workspace_assets/**/.*",
        ],
    },
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "pecs-pro=workspace_bridge_cli:main",
            "pecs=workspace_bridge_cli:main",
            "pecs-pro-daemon=run_pecs_daemon:main",
            "pecs-pro-install-workspace=install_workspace_integration:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

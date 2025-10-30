import os
import pathlib
import subprocess
from string import Template


def render_dsx(template_path: pathlib.Path, output_path: pathlib.Path, context: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    raw = template_path.read_text(encoding="utf-8")
    dsx = Template(raw).substitute(context)
    output_path.write_text(dsx, encoding="utf-8")


def run_cmd(args: list[str]) -> None:
    subprocess.run(args, check=True)


def main() -> None:
    # Environment
    domain = os.environ["DS_DOMAIN"]  # e.g., domain.host:9080
    user = os.environ["DS_USER"]
    password = os.environ["DS_PASS"]
    asb_host = os.environ["DS_ASBHOST"]  # e.g., asbnode1.company.com
    project = os.environ.get("DS_PROJECT", "BIDW_ADM")

    base = pathlib.Path(__file__).resolve().parents[1]
    template = base / "templates" / "cd_sales_payment_detail_template.dsx"
    build_out = base / "build" / "cd_sales_payment_detail.dsx"

    # Context for templating
    ctx = {
        "DS_SERVER_NAME": asb_host,
        "DS_PROJECT": project,
        "EXPORT_DATE": os.environ.get("EXPORT_DATE", "2025-10-30"),
        "EXPORT_TIME": os.environ.get("EXPORT_TIME", "13.38.34"),
        "JOB_NAME": os.environ.get("JOB_NAME", "DM_SP_SL_PAY_D_LOAD"),
        # Source is DW schema now (full copy from ODS into DM)
        "SOURCE_PARAM": os.environ.get("SOURCE_PARAM", "P_DW_VER"),
        "SOURCE_SQL": os.environ.get(
            "SOURCE_SQL",
            "SELECT * FROM BIDWADM_CO.OD_SP_SL_PAY_D",
        ),
        "TARGET_SCHEMA": os.environ.get("TARGET_SCHEMA", "BIDWADM"),
        "TARGET_TABLE": os.environ.get("TARGET_TABLE", "DM_SP_SL_PAY_D"),
    }

    # 1) Render DSX
    render_dsx(template, build_out, ctx)

    # 2) Import (overwrite)
    run_cmd([
        "istool",
        "import",
        "-dom",
        domain,
        "-u",
        user,
        "-p",
        password,
        "-archive",
        str(build_out),
        "-overwrite",
    ])

    # 3) Compile
    run_cmd([
        "dsjob",
        "-server",
        asb_host,
        "-user",
        user,
        "-password",
        password,
        "-compile",
        project,
        ctx["JOB_NAME"],
    ])

    # 4) Run (full-load, no date parameters)
    run_args = [
        "dsjob",
        "-run",
        "-server",
        asb_host,
        "-user",
        user,
        "-password",
        password,
    ]

    run_args += [project, ctx["JOB_NAME"]]
    run_cmd(run_args)

    # 5) Job info
    run_cmd([
        "dsjob",
        "-jobinfo",
        "-server",
        asb_host,
        "-user",
        user,
        "-password",
        password,
        project,
        ctx["JOB_NAME"],
    ])


if __name__ == "__main__":
    main()



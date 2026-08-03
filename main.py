"""
CLI de entrada.

Exemplos:
    python main.py "Northwestern University" --faculty-config northwestern_cs --field "Computer Science"
    python main.py "Northwestern University" --faculty-config northwestern_cs --interests "human-computer interaction"
    python main.py "Northwestern University" --faculty-config northwestern_cs --field "Computer Science" --no-cache
    python main.py --batch
    python main.py --batch --interests "human-computer interaction" "entrepreneurship"
    python main.py "Northwestern University" --faculty-config northwestern_cs --html
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src import cache
from src.comparativo import generate_comparative_report
from src.orchestrator import research_university, save_report, OUTPUT_DIR
from src.student_profile import StudentProfile

WATCHLIST_PATH = Path(__file__).parent / "data" / "watchlist.json"

console = Console()


def _load_watchlist() -> list[dict]:
    with open(WATCHLIST_PATH, encoding="utf-8") as f:
        return json.load(f)["universities"]


def _make_progress_callback() -> tuple[callable, Text]:
    """Cria um callback de progresso e o objeto Text compartilhado."""
    status_text = Text("")

    def on_progress(msg: str) -> None:
        status_text.plain = msg

    return on_progress, status_text


def _export_html(md_content: str, output_path: Path) -> Path:
    """Converte Markdown para HTML e salva."""
    import markdown2

    html_body = markdown2.markdown(
        md_content,
        extras=["tables", "fenced-code-blocks", "header-ids"],
    )
    html_path = output_path.with_suffix(".html")
    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{output_path.stem}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         max-width: 900px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6;
         color: #1a1a1a; background: #fafafa; }}
  h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 0.3rem; }}
  h2 {{ color: #1e40af; margin-top: 2rem; }}
  h3 {{ color: #334155; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
  th, td {{ border: 1px solid #d1d5db; padding: 0.5rem 0.75rem; text-align: left; }}
  th {{ background: #f1f5f9; font-weight: 600; }}
  tr:nth-child(even) {{ background: #f8fafc; }}
  a {{ color: #2563eb; }}
  blockquote {{ border-left: 4px solid #93c5fd; margin: 1rem 0; padding: 0.5rem 1rem;
               background: #eff6ff; }}
  code {{ background: #f1f5f9; padding: 0.1rem 0.3rem; border-radius: 3px; font-size: 0.9em; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    html_path.write_text(html_doc, encoding="utf-8")
    return html_path


def _run_single(args: argparse.Namespace) -> None:
    profile = None
    if args.interests:
        profile = StudentProfile(interests=args.interests, goal=args.goal)

    on_progress, status_text = _make_progress_callback()

    start = time.time()

    with Live(Panel(status_text, title=f"[bold blue]{args.university}[/]", border_style="blue"),
              console=console, refresh_per_second=4):
        report = research_university(
            university_name=args.university,
            faculty_config_key=args.faculty_config,
            field_of_interest=args.field,
            max_professors_for_research=args.max_professors,
            student_profile=profile,
            on_progress=on_progress,
        )

    elapsed = time.time() - start

    path = save_report(args.university, report)
    console.print(f"\n[green]✓[/] Relatório salvo em: [bold]{path}[/] ({elapsed:.1f}s)")

    if args.html:
        html_path = _export_html(report, path)
        console.print(f"[green]✓[/] HTML salvo em: [bold]{html_path}[/]")

    console.print()
    console.print(report)


def _run_batch(args: argparse.Namespace) -> None:
    watchlist = _load_watchlist()
    if not watchlist:
        console.print("[red]Watchlist vazia.[/] Adicione universidades em data/watchlist.json.")
        return

    profile = None
    if args.interests:
        profile = StudentProfile(interests=args.interests, goal=args.goal)

    university_names: list[str] = []
    total_start = time.time()

    for idx, entry in enumerate(watchlist, 1):
        name = entry["name"]
        university_names.append(name)

        on_progress, status_text = _make_progress_callback()

        console.rule(f"[bold blue]{name}[/] ({idx}/{len(watchlist)})")

        start = time.time()
        with Live(Panel(status_text, title=f"[blue]{name}[/]", border_style="dim"),
                  console=console, refresh_per_second=4):
            report = research_university(
                university_name=name,
                faculty_config_key=entry.get("faculty_config_key"),
                field_of_interest=entry.get("field"),
                max_professors_for_research=args.max_professors,
                student_profile=profile,
                on_progress=on_progress,
            )
        elapsed = time.time() - start

        path = save_report(name, report)
        console.print(f"  [green]✓[/] Salvo: {path} ({elapsed:.1f}s)")

        if args.html:
            html_path = _export_html(report, path)
            console.print(f"  [green]✓[/] HTML: {html_path}")

    # Gerar comparativo
    console.rule("[bold]Relatório Comparativo[/]")

    comparative = generate_comparative_report(university_names)
    OUTPUT_DIR.mkdir(exist_ok=True)
    comp_path = OUTPUT_DIR / "comparativo.md"
    comp_path.write_text(comparative, encoding="utf-8")

    if args.html:
        html_comp = _export_html(comparative, comp_path)
        console.print(f"  [green]✓[/] HTML comparativo: {html_comp}")

    total_elapsed = time.time() - total_start
    console.print(f"\n[green]✓[/] Comparativo salvo: [bold]{comp_path}[/]")
    console.print(f"  Tempo total: {total_elapsed:.1f}s")
    console.print()
    console.print(comparative)


def main() -> None:
    load_dotenv()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Pesquisa profunda sobre universidades dos EUA.")
    parser.add_argument("university", nargs="?", default=None,
                        help="Nome exato da universidade (como aparece no College Scorecard).")
    parser.add_argument("--batch", action="store_true",
                        help="Roda todas as universidades de data/watchlist.json e gera comparativo.")
    parser.add_argument("--faculty-config", default=None, help="Chave em data/faculty_configs.json.")
    parser.add_argument("--field", default=None, help="Área de interesse (ex: 'Computer Science').")
    parser.add_argument("--interests", nargs="+", default=None,
                        help="Áreas de interesse do aluno para ranquear professores.")
    parser.add_argument("--goal", default="research",
                        choices=["research", "industry", "entrepreneurship"],
                        help="Objetivo do aluno.")
    parser.add_argument("--max-professors", type=int, default=5)
    parser.add_argument("--no-cache", action="store_true",
                        help="Ignora cache local e busca tudo de novo nas APIs.")
    parser.add_argument("--html", action="store_true",
                        help="Gera também uma versão HTML do relatório.")
    args = parser.parse_args()

    if args.no_cache:
        cache.set_enabled(False)

    if args.batch:
        _run_batch(args)
    elif args.university:
        _run_single(args)
    else:
        parser.error("Informe o nome de uma universidade ou use --batch.")


if __name__ == "__main__":
    main()

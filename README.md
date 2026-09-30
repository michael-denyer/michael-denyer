<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/michael-denyer/michael-denyer/output/profile-banner-night.svg">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/michael-denyer/michael-denyer/output/profile-banner-day.svg">
    <img src="https://raw.githubusercontent.com/michael-denyer/michael-denyer/output/profile-banner-day.svg" width="100%" alt="Michael Denyer, scientific Python, genomics, data engineering, AI, and repository stars">
  </picture>
</p>

I build bioinformatics and AI tools for the jobs that eat your afternoon: slow analyses, unfamiliar codebases, and agents that need the same explanation again. Mostly Python and C, with occasional detours into [cats](https://michael-denyer.github.io/) and [cosmic destruction](https://michael-denyer.github.io/everything-must-go/).

![Python](https://img.shields.io/badge/Python-1f6f8b?style=flat-square&logo=python&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-17324d?style=flat-square&logo=rust&logoColor=white)
![C](https://img.shields.io/badge/C-526878?style=flat-square&logo=c&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-f06a3c?style=flat-square&logo=apachespark&logoColor=white)
![Databricks](https://img.shields.io/badge/Databricks-d94f32?style=flat-square&logo=databricks&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2d8fb0?style=flat-square&logo=docker&logoColor=white)

[Bioinformatics](#bioinformatics) · [AI development](#ai-development) · [Other apps](#other-apps) · [Contributions](#open-source-contributions) · [Website](https://michael-denyer.github.io/)

## Bioinformatics

<table width="100%">
  <tr>
    <td>
      <h3><a href="https://github.com/michael-denyer/jamma"><img src="https://raw.githubusercontent.com/michael-denyer/jamma/master/logos/JAMMA_Large_Logo_v2.png" height="64" align="middle" alt="">&nbsp;&nbsp;&nbsp;JAMMA</a></h3>
      <p>Get more GWAS done with the compute you have. JAMMA accelerates kinship and association testing with native C kernels, processes genotypes in chunks to control memory use, and reuses eigendecompositions across phenotypes. Keep familiar GEMMA commands or use the Python API.</p>
      <p><a href="https://pypi.org/project/jamma/">PyPI</a> · <a href="https://github.com/michael-denyer/jamma#performance">Benchmarks</a> · <a href="https://github.com/michael-denyer/jamma-lean-proofs">Lean 4 proofs</a></p>
      <p><sub>My <a href="https://github.com/michael-denyer/numpy-mkl">numpy-mkl fork</a> builds Intel MKL NumPy and SciPy wheels with 64-bit NumPy indexing for much larger GWAS.</sub></p>
    </td>
  </tr>
  <tr>
    <td>
      <h3><a href="https://github.com/michael-denyer/fast-beagle-5.5"><img src="https://raw.githubusercontent.com/michael-denyer/fast-beagle-5.5/main/docs/logo.jpg" height="64" align="middle" alt="">&nbsp;&nbsp;&nbsp;Fast Beagle</a></h3>
      <p>Phase and impute larger cohorts with less waiting and less RAM. These C ports of Beagle 5.4 and 5.5 preserve each Java release's VCF output byte for byte at the same thread count, and add BGEN output. The 5.5 benchmarks show 1.5× to over 3× faster runs, with memory use reduced by up to 3.5×.</p>
      <p><a href="https://github.com/michael-denyer/fast-beagle-5.5">Beagle 5.5 edition</a> · <a href="https://github.com/michael-denyer/fast-beagle-5.4">Beagle 5.4 edition</a> · <a href="https://github.com/michael-denyer/fast-beagle-5.5/blob/main/docs/perf-baseline.md">Benchmarks</a></p>
    </td>
  </tr>
  <tr>
    <td>
      <h3><a href="https://github.com/michael-denyer/pyLocusZoom"><img src="https://raw.githubusercontent.com/michael-denyer/pyLocusZoom/main/logo.svg" height="64" align="middle" alt="">&nbsp;&nbsp;&nbsp;pyLocusZoom</a></h3>
      <p>Give your GWAS hits some context. Turn result tables into publication-ready figures or interactive plots, with LD, genes, and fine-mapping evidence alongside the association signal. Works with Pandas or PySpark, with built-in dog and cat references and support for other species.</p>
      <p><a href="https://pypi.org/project/pylocuszoom/">PyPI</a> · <a href="https://github.com/michael-denyer/pyLocusZoom#gallery">Plot gallery</a></p>
      <p><a href="https://github.com/michael-denyer/pyLocusZoom"><img src="images/manhattan_qq_sidebyside.png" width="100%" alt="Manhattan and QQ plots produced with pyLocusZoom"></a></p>
      <p><sub>Manhattan and QQ plots produced with pyLocusZoom.</sub></p>
    </td>
  </tr>
</table>

## AI development

<table width="100%">
  <tr>
    <td width="50%" valign="top">
      <h3><img src="images/icons/workflow.svg" width="28" height="28" alt=""> <a href="https://github.com/michael-denyer/pstack-claude">pstack</a> <img src="images/badges/popular.svg" width="76" height="20" alt="Popular"></h3>
      <p>Make your coding agent earn its "done". Pstack gives it workflows to reproduce bugs, challenge designs, review changes, and verify the result. My port of Lauren Tan's pstack brings that discipline to the agents below.</p>
      <p><sub>Claude Code · Codex · OpenCode · Gemini CLI · Prime Agent</sub></p>
    </td>
    <td width="50%" valign="top">
      <h3><img src="images/icons/memory.svg" width="28" height="28" alt=""> <a href="https://github.com/michael-denyer/memory-mcp">Memory MCP</a></h3>
      <p>Your assistant should remember why you made that decision. Memory MCP carries project knowledge between sessions, puts frequently used facts straight into Claude Code's context, and retrieves the rest by meaning.</p>
      <p><sub>Hot cache · Semantic search · Knowledge graph</sub></p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3><img src="images/icons/code.svg" width="28" height="28" alt=""> Language servers</h3>
      <p>Help Claude Code follow definitions and references across Python, Terraform, and linked Markdown docs. Pyrefly also provides fast Python type checking, giving the agent more to work with when fixing errors.</p>
      <p><a href="https://github.com/michael-denyer/pyrefly-lsp-cc-plugin">Pyrefly</a> · <a href="https://github.com/michael-denyer/terraform-lsp-cc-plugin">Terraform</a> · <a href="https://github.com/michael-denyer/marksman-lsp-cc-plugin">Marksman</a></p>
    </td>
    <td width="50%" valign="top">
      <h3><img src="images/icons/chip.svg" width="28" height="28" alt=""> <a href="https://github.com/michael-denyer/bonsai-agent">bonsai-agent</a></h3>
      <p>Give Claude Code a local helper. Delegate tasks to a Bonsai 2 27B model running on your Apple Silicon Mac through MLX. The server starts on demand and shuts down when idle, so you don't have to babysit it.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3><img src="images/icons/message.svg" width="28" height="28" alt=""> <a href="https://github.com/michael-denyer/signal-output-style">Signal</a></h3>
      <p>Claude has plenty to say. Signal helps it get to the point, with answers first, explanations sized to the question, and numbers backed by units and sources. A small output style for Claude Code.</p>
    </td>
    <td width="50%" valign="top">
      <h3><img src="images/icons/history.svg" width="28" height="28" alt=""> <a href="https://github.com/michael-denyer/claude-mem-lean">claude-mem-lean</a></h3>
      <p>Pick up where the last session left off. My Claude-Mem fork captures tool activity and compresses it into summaries, so Claude can recover what happened without rereading the whole conversation.</p>
    </td>
  </tr>
</table>

## Other apps

<table width="100%">
  <tr>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/michael-denyer/black-box-unlock">Black Box Unlock</a></h3>
      <p align="center"><a href="https://github.com/michael-denyer/black-box-unlock"><img src="https://raw.githubusercontent.com/michael-denyer/black-box-unlock/main/assets/logo.png" height="150" alt="Black Box Unlock"></a></p>
      <p>Investigate your codebase like a crime scene. Black Box Unlock combines change history, hidden coupling, ownership, and CI failures to help you choose what to review or refactor first. Use it from the CLI or give coding agents direct access through MCP.</p>
    </td>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/michael-denyer/everything-must-go">Everything Must Go</a></h3>
      <p align="center"><a href="https://michael-denyer.github.io/everything-must-go/"><img src="https://raw.githubusercontent.com/michael-denyer/everything-must-go/main/public/og.jpg" height="150" alt="A black hole consuming a procedurally generated cosmos"></a></p>
      <p>An interactive WebGL apocalypse. A spinning black hole consumes a procedural cosmos over twelve minutes, then a new universe takes its place. Stir the gas, feed the black hole, or just watch it all go.</p>
      <p><a href="https://michael-denyer.github.io/everything-must-go/">Feed the black hole</a></p>
    </td>
  </tr>
</table>

[The Aether Works](https://github.com/michael-denyer/michael-denyer.github.io) is my personal site, disguised as a steampunk workshop. There are cats, animated machinery, and gauges fed by GitHub activity. [Step inside](https://michael-denyer.github.io/).

## Open-source contributions

| Project | Contributions |
| :--- | :--- |
| [colibri](https://github.com/JustVugg/colibri) | Helping a tiny C inference engine run better on ARM, with kernel, profiling, portability, and memory-management fixes. [Pull requests](https://github.com/JustVugg/colibri/pulls?q=is%3Apr+author%3Amichael-denyer). |
| [code-review-graph](https://github.com/tirth8205/code-review-graph) | Teaching a code knowledge graph to read R and notebooks, and fixing how it tracks calls at module scope. [Pull requests](https://github.com/tirth8205/code-review-graph/pulls?q=is%3Apr+author%3Amichael-denyer). |
| [qqman](https://github.com/satchellhong/qqman) | Modernised the Python package for Python 3.10+. [Pull request](https://github.com/satchellhong/qqman/pull/3). |

---

<div align="center">
  <h3>Meanwhile, at the Commit Café...</h3>
  <p><sub>Repositories become cats, recent commits become yarn, open pull requests wait at the door, and the contribution streak fills the food bowl.</sub></p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/michael-denyer/michael-denyer/output/cafe-night.svg?v=12">
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/michael-denyer/michael-denyer/output/cafe-day.svg?v=12">
    <img src="https://raw.githubusercontent.com/michael-denyer/michael-denyer/output/cafe-day.svg?v=12" width="100%" alt="The Commit Café: animated cats represent repository activity, a dog represents open pull requests, and a bowl represents the contribution streak">
  </picture>
</div>

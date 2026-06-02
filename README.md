# armbian-compile-action

GitHub Action for Armbian [`compile.sh`](https://github.com/armbian/build).

## Usage

```yaml
- uses: winddyx/armbian-compile-action@main
  with:
    board: nanopineo
    distro: debian
    suite: trixie       # optional, overrides default release mapping
    flavor: cli          # cli = minimal, or desktop name (kde, cinnamon, etc.)
    artifacts: 'true'    # optional, upload build artifacts
```

### Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `board` | ✅ | — | Armbian board name (e.g. `nanopineo`, `orangepizero`) |
| `distro` | ✅ | — | `debian` or `ubuntu` (used when `suite` is not set) |
| `suite` | ❌ | — | Override release name (e.g. `trixie`, `bookworm`, `noble`). When empty, maps `debian→bullseye`, `ubuntu→jammy` |
| `flavor` | ✅ | — | `cli` for minimal headless, or desktop name (`kde`, `cinnamon`, etc.) |
| `kernel_branch` | ❌ | `current` | Kernel branch (`current`, `edge`, `vendor`) |
| `armbian_ref` | ❌ | `v26.2.1` | Armbian build framework git ref (tag/branch/commit) |
| `artifacts` | ❌ | `false` | Upload built images as workflow artifacts |
| `release-id` | ❌ | — | GitHub Release ID to upload to |
| `github-token` | ❌ | — | `${{ secrets.GITHUB_TOKEN }}` for release upload |

### Equivalent local compile command

```bash
./compile.sh \
  BOARD=nanopineo \
  RELEASE=trixie \
  BUILD_DESKTOP=no \
  BUILD_MINIMAL=yes \
  KERNEL_CONFIGURE=no
```

maps to:

```yaml
- uses: winddyx/armbian-compile-action@main
  with:
    board: nanopineo
    distro: debian
    suite: trixie
    flavor: cli
```

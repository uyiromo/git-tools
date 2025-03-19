#!/bin/bash
set -ue
set -o pipefail

git reset

cat >.lfrules.toml <<__EOF__
# markdown
md = [ "*.md", "**/*.md" ]

# python
py = [ "*.py", "**/*.py" ]

# shell
sh = [ "*.sh", "**/*.sh" ]

# toml
toml = [ "*.toml", "**/*.toml" ]

# yaml
yaml = [ "*.yaml", "**/*.yaml", "*.yml", "**/*.yml" ]

# json
json = [ "*.json", "**/*.json" ]

# javascript
javascript = [ "*.js", "**/*.js", "*.mjs", "**/*.mjs" ]

# Dockerfile
dockerfile = [ "Dockerfile", "**/Dockerfile" ]

# NO LINT, NO FOMRMAT
none = [
  ".flake8",
  "requirements.txt",
  "**/requirements.txt",
  ".editorconfig",
  ".gitignore",
  ".gitmodules",
  "*.cron",
  ".yamlfmt"
]
__EOF__
git add .lfrules.toml

#
# Python (flake8, black)
#
cat >.flake8 <<__EOF__
[flake8]
max-line-length = 120
exclude =
    .venv/,
    .venv-runner/,
    .git,
    __pycache__
__EOF__
git add .flake8

cat >pyproject.toml <<__EOF__
[tool.black]
line-length = 120
__EOF__
git add pyproject.toml

#
# Shell (shfmt)
#
cat >.editorconfig <<__EOF__
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
__EOF__
git add .editorconfig

#
# TOML (taplo)
#
cat >.taplo.toml <<__EOF__
include = [ "**/*.toml" ]

[formatting]
align_comments        = true
align_entries         = true
allowed_blank_lines   = 2
array_auto_collapse   = false
array_auto_expand     = true
array_trailing_comma  = true
column_width          = 120
compact_arrays        = false
compact_entries       = false
compact_inline_tables = false
crlf                  = false
indent_entries        = false
indent_string         = "  "
indent_tables         = false
inline_table_expand   = true
reorder_arrays        = true
reorder_keys          = true
trailing_newline      = true
__EOF__
git add .taplo.toml

#
# YAML (yamlfmt)
#
cat >.yamlfmt <<__EOF__
formatter:
  type: basic
__EOF__
git add .yamlfmt

#
# Javascript (eslint)
#
cat >eslint.config.mjs <<__EOF__
import stylisticJs from '/usr/lib/node_modules/@stylistic/eslint-plugin-js/dist/index.js'

export default [
    {
        plugins: {
            '@stylistic/js': stylisticJs
        },
        files: ["**/*.js"],
        rules: {
            '@stylistic/js/array-bracket-newline': ['error', 'always'],
            '@stylistic/js/array-element-newline': ['error', 'always'],
            '@stylistic/js/eol-last': ['error', 'always'],
            '@stylistic/js/comma-spacing': ["error", { "before": false, "after": true }],
            '@stylistic/js/indent': ['error', 4],
            '@stylistic/js/semi': ['error', "always"]
        }
    }
];
__EOF__
git add eslint.config.mjs

git commit -m ":seedling: lf-init"

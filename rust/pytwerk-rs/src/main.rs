use std::env;
use std::io::{self, Read};
use std::process;

fn py_single_quoted_literal(input: &str) -> String {
    let mut out = String::with_capacity(input.len() + 2);
    out.push('\'');
    for ch in input.chars() {
        match ch {
            '\\' => out.push_str("\\\\"),
            '\'' => out.push_str("\\'"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            _ => out.push(ch),
        }
    }
    out.push('\'');
    out
}

fn compile_source(source: &str) -> String {
    let lines: Vec<&str> = source.lines().collect();
    let mut out: Vec<String> = Vec::with_capacity(lines.len() + 4);
    let mut i = 0usize;

    while i < lines.len() {
        let line = lines[i];
        let stripped = line.trim();

        if stripped == "return (" {
            let indent_len = line.len() - line.trim_start().len();
            let indent = &line[..indent_len];
            let mut j = i + 1;
            let mut markup_lines: Vec<&str> = Vec::new();

            while j < lines.len() {
                let candidate = lines[j];
                if candidate.trim() == ")" {
                    break;
                }
                markup_lines.push(candidate);
                j += 1;
            }

            let first_non_empty = markup_lines
                .iter()
                .find_map(|line| {
                    let trimmed = line.trim();
                    if trimmed.is_empty() {
                        None
                    } else {
                        Some(trimmed)
                    }
                })
                .unwrap_or("");

            if j < lines.len() && !markup_lines.is_empty() && first_non_empty.starts_with('<') {
                let markup = markup_lines.join("\n");
                let markup_lit = py_single_quoted_literal(&markup);
                out.push(format!("{indent}return __pytwerk_render__("));
                out.push(format!("{indent}    {markup_lit},"));
                out.push(format!("{indent}    locals(),"));
                out.push(format!("{indent}    globals(),"));
                out.push(format!("{indent})"));
                i = j + 1;
                continue;
            }
        }

        out.push(line.to_string());
        i += 1;
    }

    let compiled = out.join("\n");
    let mut final_src = format!("from pytwerk.core.runtime import __pytwerk_render__\n\n{compiled}");
    if !final_src.ends_with('\n') {
        final_src.push('\n');
    }
    final_src
}

fn read_stdin_to_string() -> io::Result<String> {
    let mut buf = String::new();
    io::stdin().read_to_string(&mut buf)?;
    Ok(buf)
}

fn print_usage() {
    eprintln!("Usage:");
    eprintln!("  pytwerk-rs compile --stdin");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 3 || args[1] != "compile" || args[2] != "--stdin" {
        print_usage();
        process::exit(2);
    }

    let source = match read_stdin_to_string() {
        Ok(s) => s,
        Err(err) => {
            eprintln!("failed to read stdin: {err}");
            process::exit(1);
        }
    };

    let compiled = compile_source(&source);
    print!("{compiled}");
}

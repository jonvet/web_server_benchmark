# Web server benchmark

This repository contains 3 self-contained python and rust projects that implement a simple web server using different frameworks.

- [Python FastAPI](python_fastapi/)
- [Rust Rocket](rust_rocket/)
- [Rust Axum](rust_axum/)

If you need more of a hands-on tutorial, check out my blog posts [How to build a simple web server in Python](https://www.jonvet.com/blog/simple-webserver-in-python) and [How to build a simple web server in Rust](https://www.jonvet.com/blog/simple-webserver-in-rust) where I go into more detail.

## Benchmark

The [benchmark](benchmark/) directory contains a script to benchmark the performance of each server, and a script to plot the results after all 3 servers have been benchmarked.

This produces the following plots:

![Single Threaded Benchmark results](benchmark/assets/webserver_benchmark_single_threaded.png)
![Multi Threaded Benchmark results](benchmark/assets/webserver_benchmark_multi_threaded.png)


If you like, check out my blog post on this comparison [Benchmarking Python and Rust web servers](https://www.jonvet.com/blog/benchmarking-python-rust-web-servers).
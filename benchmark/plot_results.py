import json
import matplotlib.pyplot as plt
import numpy as np


def create_bar_chart(python_results, rocket_results, axum_results, thread_type):
    operations = list(python_results.keys())

    # Prepare data based on thread type
    data = {
        "Python": [python_results[op][thread_type] for op in operations],
        "Rocket": [rocket_results[op][thread_type] for op in operations],
        "Axum": [axum_results[op][thread_type] for op in operations],
    }

    # Sorting within the group
    sorted_data = {
        op: sorted(
            [(key, value[i]) for key, value in data.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        for i, op in enumerate(operations)
    }

    x = np.arange(len(operations))
    width = 0.25  # Width of the bars

    plt.rcParams.update({"font.size": 14})  # Increase the default font size

    fig, ax = plt.subplots(figsize=(20, 8))  # Increased figure size

    color_map = {
        "Python": "navy",
        "Rocket": "darkred",
        "Axum": "seagreen",
    }

    for i, op in enumerate(operations):
        # Plot results based on the thread type
        for j, (label, value) in enumerate(sorted_data[op]):
            bar = ax.bar(
                x[i] + j * width - width,
                value,
                width,
                label=(
                    f'{label} {thread_type.replace("_", " ").title()}'
                    if i == 0
                    else None
                ),
                color=color_map[label],
            )
            # Add data labels inside the bars with white color and larger font
            ax.bar_label(bar, fmt="%.2f", padding=-20, color="white", fontsize=16)

    ax.set_ylabel("Time (milliseconds per operation)", fontsize=18)
    ax.set_title(
        f'Benchmark: Python vs Rust servers - {thread_type.replace("_", " ").title()}',
        fontsize=22,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(operations, fontsize=18)
    ax.tick_params(axis="y", labelsize=14)
    ax.set_ylim(0, 3)  # Set y-axis limit from 0 to 3
    ax.legend(loc="upper left", fontsize=18)

    plt.tight_layout()
    plt.savefig(f"webserver_benchmark_{thread_type}_release.png", dpi=200)
    print(
        f"{thread_type.replace('_', ' ').title()} bar chart saved as 'benchmark_comparison_{thread_type}_release.png'"
    )


if __name__ == "__main__":
    with open("benchmark_results_python.json", "r") as f:
        python_results = json.load(f)
    with open("benchmark_results_rocket.json", "r") as f:
        rocket_results = json.load(f)
    with open("benchmark_results_axum.json", "r") as f:
        axum_results = json.load(f)

    # Create single-threaded chart
    create_bar_chart(python_results, rocket_results, axum_results, "single_threaded")

    # Create multi-threaded chart
    create_bar_chart(python_results, rocket_results, axum_results, "multi_threaded")

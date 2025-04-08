import matplotlib.pyplot as plt
import networkx as nx



def visualize_vhpop_output_layered_with_start(output: str, save_path: str = "vhpop_plan.png") -> None:
    """Visualize VHPOP plan with same-timestep actions aligned horizontally and virtual start node."""
    import collections

    G = nx.DiGraph()
    timestep_to_actions = collections.OrderedDict()

    # Parse the output into timestep-indexed actions
    for line in output.splitlines():
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        try:
            timestep_str, action_str = line.split(":", 1)
            timestep = int(timestep_str.strip())
            action = action_str.strip()
            if timestep not in timestep_to_actions:
                timestep_to_actions[timestep] = []
            timestep_to_actions[timestep].append(action)
        except ValueError:
            continue
    print(timestep_to_actions)

    if not timestep_to_actions:
        print("⚠️ No actions parsed from VHPOP output.")
        return

    # Insert virtual start node at timestep 0
    G.add_node("0:start", label="start", layer=0)

    # Add all nodes and store their positions
    node_ids = []
    for timestep, actions in timestep_to_actions.items():
        for i, action in enumerate(actions):
            node_id = f"{timestep}:{i}"
            label = f"{action}"
            G.add_node(node_id, label=label, layer=timestep)
            node_ids.append((timestep, i, node_id, action))

    # Connect start node to all timestep 1 actions
    first_real_timestep = min(timestep_to_actions.keys())
    for i, _ in enumerate(timestep_to_actions[first_real_timestep]):
        G.add_edge("0:start", f"{first_real_timestep}:{i}")

    # Connect matched index actions from t → t+1
    timestep_list = list(timestep_to_actions.items())
    for i in range(len(timestep_list) - 1):
        curr_timestep, curr_actions = timestep_list[i]
        next_timestep, next_actions = timestep_list[i + 1]
        #if len(current)==len(next), connect corresponding actions
        if len(curr_actions)==len(next_actions):
            for j in range(len(curr_actions)):
                G.add_edge(f"{curr_timestep}:{j}", f"{next_timestep}:{j}")
        else:
            #if len(current)!=len(next), connect all actions of current to all actions of next
            for j in range(len(curr_actions)):
                for k in range(len(next_actions)):
                    G.add_edge(f"{curr_timestep}:{j}", f"{next_timestep}:{k}")

        # for j in range(min(len(curr_actions), len(next_actions))):
        #     src = f"{curr_timestep}:{j}"
        #     dst = f"{next_timestep}:{j}"
        #     G.add_edge(src, dst)
    # Custom layout: align same timestep horizontally
    pos = {}
    x_spacing = 0.025# make actions closer
    num_layers = len(timestep_to_actions) + 1
    y_spacing = 1

    # Determine maximum number of parallel actions (widest layer)
    max_width = max(len(actions) for actions in timestep_to_actions.values())
    #max actions length
    max_action_length = max(len(action) for action in timestep_to_actions.values())
    print(max_action_length)
    total_width = max_width * max_action_length+2

    # Centered start node
    pos["0:start"] = (total_width / 2, 0)

    for layer_idx, (timestep, actions) in enumerate(timestep_to_actions.items(), start=1):
        n_actions = len(actions)
        row_width = (n_actions - 1) * x_spacing
        x_start = (total_width - row_width) / 2
        for i, _ in enumerate(actions):
            node_id = f"{timestep}:{i}"
            pos[node_id] = (x_start + i * x_spacing, -layer_idx * y_spacing)

    # Automatically scale figure size
    fig_width = min(20, total_width)
    print(fig_width)
    fig_height = max(5, num_layers * y_spacing * 0.9)

    # # Layout settings
    # x_spacing = 3
    # y_spacing = 2
    # num_layers = len(timestep_to_actions) + 1  # +1 for start
    # max_width = max(len(v) for v in timestep_to_actions.values())

    # pos = {}

    # # Position action nodes
    # for layer_idx, (timestep, actions) in enumerate(timestep_to_actions.items(), start=1):
    #     width = len(actions)
    #     for i, _ in enumerate(actions):
    #         # If only one node in this timestep → center
    #         if width == 1:
    #             x = (max_width - 1) * x_spacing / 2
    #         else:
    #             x = i * x_spacing
    #         y = -layer_idx * y_spacing
    #         node_id = f"{timestep}:{i}"
    #         pos[node_id] = (x, y)

    # # Center start node
    # first_layer_width = len(timestep_to_actions[first_real_timestep])
    # start_x = ((first_layer_width - 1) * x_spacing) / 2
    # pos["0:start"] = (start_x, 0)

    # # Draw graph
    # fig_height = y_spacing * (num_layers + 1) / 2
    # fig_width = max(10, x_spacing * (max_width + 1))
    plt.figure(figsize=(fig_width, fig_height))

    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2200)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20)
    labels = {n: G.nodes[n]['label'] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    plt.title("VHPOP Plan Visualization (Layered, Centered)", fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

    print(f"✅ Saved nicely aligned plan to: {save_path}")
    


if __name__ == "__main__":
    # Read the output file
    output_file = "/home/veronica/Documents/Semantic_Action_Recognition/task_planning/predicators/predicators/third_party/vhpop/vhpop_output.txt"
    save_path = "/home/veronica/Documents/Semantic_Action_Recognition/task_planning/predicators/predicators/third_party/vhpop/vhpop_plan.png"
    
    with open(output_file, 'r') as f:
        output = f.read()
    
    visualize_vhpop_output_layered_with_start(output, save_path)
    #run_visualization_test()
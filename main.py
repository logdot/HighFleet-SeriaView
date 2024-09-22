from tkinter import *
from tkinter import ttk, filedialog
from seria_tree import *


class SeriaView:
    def __init__(self):
        # Data model
        self.profile: SeriaTree = None
        # self.show_escadra = True
        # self.show_location = True
        # self.show_npc = True

        # UI
        self.root_window = Tk()
        self.root_window.title("SeriaView - by DKAMX")
        self.root_window.minsize(640, 480)

        self.treeview: ttk.Treeview = None
        self.detail_text: Text = None

        self._create_menu_bar()
        self._create_treeview()

        self.root_window.mainloop()

    def _create_menu_bar(self):
        menu_bar = Menu(self.root_window)
        self.root_window.config(menu=menu_bar)

        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self._open_file)
        file_menu.add_command(label="Close", command=self._close_file)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # view_menu = Menu(menu_bar, tearoff=0)
        # view_menu.add_command(label="Expand all")
        # view_menu.add_command(label="Collapse all")
        # view_menu.add_command(label="Expand selected")
        # view_menu.add_command(label="Collapse selected")
        # menu_bar.add_cascade(label="View", menu=view_menu)

        # filter_menu = Menu(menu_bar, tearoff=0)
        # menu_bar.add_cascade(label="Filter", menu=filter_menu)

    def _create_treeview(self):
        tree_frame = Frame(self.root_window, padx=5, pady=5)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(2, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        self.treeview = ttk.Treeview(tree_frame, show="tree")
        self.treeview.grid(row=0, column=0, sticky=NSEW)
        self.treeview.bind("<<TreeviewSelect>>", self._on_tree_select)

        tree_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.treeview.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=NS)
        self.treeview.config(yscrollcommand=tree_scrollbar.set)

        self.detail_text = Text(tree_frame, width=40)
        self.detail_text.insert('end', 'Open a file to view details')
        self.detail_text.config(state=DISABLED)
        self.detail_text.grid(row=0, column=2, sticky=NSEW)

        text_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.detail_text.yview)
        text_scrollbar.grid(row=0, column=3, sticky=NS)
        self.detail_text.config(yscrollcommand=text_scrollbar.set)

        tree_frame.pack(expand=True, fill=BOTH)

    # File menu actions
    def _open_file(self):
        filename = filedialog.askopenfilename()
        if isinstance(filename, tuple):
            return

        try:
            self.profile = SeriaTree(filename)
        except Exception:
            return

        self._clear_treeview()

        self.profile.build(readAttributeFilter('attribute_filter.json'))

        self._load_tree(self.profile.tree.root, '')
        self.treeview.item(self.profile.tree.root, open=True)

        self.detail_text.config(state=NORMAL)
        self.detail_text.delete('1.0', 'end')
        self.detail_text.insert('end', 'Select a node to view details')
        self.detail_text.config(state=DISABLED)

    def _close_file(self):
        if self.profile is not None:
            self.profile.__exit__()

        self._clear_treeview()

    def _load_tree(self, node_id, parent_id, depth=0, max_depth=3):
        if depth > max_depth:
            return

        node = self.profile.tree.get_node(node_id)

        self.treeview.insert(parent_id, 'end', node_id,
                             text=getNodeHeading(node))

        children = self.profile.tree.children(node_id)
        for child in children:
            self._load_tree(child.identifier, node_id, depth + 1)

    # Treeview actions
    def _clear_treeview(self):
        self.detail_text.config(state=NORMAL)
        self.detail_text.delete('1.0', 'end')
        self.detail_text.insert('end', 'Open a file to view details')
        self.detail_text.config(state=DISABLED)

        self.treeview.delete(*self.treeview.get_children())

    def _on_tree_select(self, event):
        self.detail_text.config(state=NORMAL)
        self.detail_text.delete('1.0', 'end')

        node_id = event.widget.focus()
        node = self.profile.tree.get_node(node_id)

        self.detail_text.insert('end', getNodeSummary(node))
        self.detail_text.config(state=DISABLED)


def getNodeHeading(node: Node):
    classname = node.tag
    if classname == 'Escadra':
        name = node.data['m_name'][1]
        if name == 'MARK' or name == 'DETACHMENT':
            return f"Escadra: {name} [Player]"
        return f"Fleet: {name}"
    if classname == 'Location':
        return f"City: {node.data['m_name'][1]} - {node.data['m_codename'][1]}"
    if classname == 'NPC':
        if 'm_tarkhan' in node.data:
            return f"NPC: {node.data['m_fullname'][1]}"
    if classname == 'Node':
        if 'm_name' in node.data:
            return f"{classname} {node.data['m_name'][1]}"
    return classname


def getNodeSummary(node: Node):
    if node.data is None:
        return None

    output = ''
    for item in node.data.items():
        attribute_name = item[0]
        value = item[1]

        if attribute_name == 'Header' or attribute_name == 'LineIndex':
            output += f"{attribute_name}: {value}\n"
        else:
            if isinstance(value, list):
                output += f"{attribute_name}:\n"
                for v in value:
                    output += f" {v[1]}\n"
            else:
                output += f"{item[0]}: {item[1][1]}\n"

    return output


if __name__ == "__main__":
    SeriaView()

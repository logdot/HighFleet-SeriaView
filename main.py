from tkinter import *
from tkinter import filedialog, ttk
import seria

__author__ = 'Max'
__version__ = '0.1.0'


class SeriaController:
    def __init__(self):
        # Data model
        self.seria: seria.SeriaNode = None

        # GUI
        self.root = Tk()
        self.root.title(f'SeriaView v{__version__}')
        self.root.minsize(640, 480)

        self.treeview: ttk.Treeview = None
        self.text_detail: Text = None

        self._make_menu()
        self._make_treeview()
        # TODO base view
        # TODO map view

        self.root.mainloop()

    def _make_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        menu_file = Menu(menubar, tearoff=0)
        menu_file.add_command(label='Open', command=self.open_file)
        menu_file.add_command(label='Close', command=self.close_file)
        menubar.add_cascade(label='File', menu=menu_file)

    def _make_treeview(self):
        frm_tree = ttk.Frame(self.root)
        frm_tree.grid_columnconfigure(0, weight=1)
        frm_tree.grid_columnconfigure(2, weight=1)
        frm_tree.grid_rowconfigure(0, weight=1)

        self.treeview = ttk.Treeview(frm_tree, show='tree')
        self.treeview.grid(row=0, column=0,
                           sticky=NSEW)

        sb_tree = ttk.Scrollbar(frm_tree, orient='vertical',
                                command=self.treeview.yview)
        sb_tree.grid(row=0, column=1,
                     sticky=NS)
        self.treeview.config(yscrollcommand=sb_tree.set)

        self.text_detail = Text(frm_tree, width=40)
        self.text_detail.insert('end', 'Open a file to view details')
        self.text_detail.config(state=DISABLED)
        self.text_detail.grid(row=0, column=2,
                              sticky=NSEW)

        sb_detail = ttk.Scrollbar(
            frm_tree, orient='vertical', command=self.text_detail.yview)
        sb_detail.grid(row=0, column=3,
                       sticky=NS)
        self.text_detail.config(yscrollcommand=sb_detail.set)

        frm_tree.pack(expand=True, fill=BOTH)

        self.treeview.bind('<<TreeviewSelect>>', self._on_treeview_select)

    def _update_treeview(self):
        def summary(node: seria.SeriaNode):
            classname = node.get_attribute('m_classname')
            name = node.get_attribute('m_name')
            codename = node.get_attribute('m_codename')
            fullname = node.get_attribute('m_fullname')
            is_tarkhan = node.get_attribute('m_tarkhan')
            code = node.get_attribute('m_code')

            if classname == 'Escadra':
                return f'Squadron {name}'
            elif classname == 'Location':
                return f'City {name} ({codename})'
            elif classname == 'NPC':
                return f'{classname} {fullname}' if is_tarkhan else classname
            elif classname == 'Node':
                return f'{classname} {name}' if code == '7' else classname
            elif classname == 'Body':
                return f'{classname} {name}' if name else classname
            return classname

        def add_children(node: seria.SeriaNode, parent_id: str):
            node_id = self.treeview.insert(
                parent_id, 'end', text=summary(node))
            for child in node.get_nodes():
                add_children(child, node_id)

        self.treeview.delete(*self.treeview.get_children())
        root_id = self.treeview.insert('', 'end', text=summary(self.seria))

        for node in self.seria.get_nodes():
            add_children(node, root_id)

        self.treeview.item(root_id, open=True)

    def _on_treeview_select(self, event):
        def _show_node_attributes(node: seria.SeriaNode):
            self.text_detail.config(state=NORMAL)
            self.text_detail.delete(1.0, END)
            for key, value in node.get_attributes().items():
                self.text_detail.insert('end', f'{key}: {value}\n')
            self.text_detail.config(state=DISABLED)

        node_id = event.widget.focus()
        parent_id = self.treeview.parent(node_id)

        if parent_id == '':
            _show_node_attributes(self.seria)
            return

        # node index sequence (from root to selected node)
        index_sequence = []
        while parent_id != '':
            index_sequence.insert(0, self.treeview.index(node_id))
            node_id = parent_id
            parent_id = self.treeview.parent(node_id)

        node = self.seria
        for index in index_sequence:
            node = node.get_node(index)

        _show_node_attributes(node)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Seria files', '*.seria')])
        if file_path:
            self.seria = seria.load(file_path)
            self._update_treeview()

    def close_file(self):
        self.seria = None
        self.treeview.delete(*self.treeview.get_children())
        self.text_detail.config(state=NORMAL)
        self.text_detail.delete(1.0, END)
        self.text_detail.insert('end', 'Open a file to view details')
        self.text_detail.config(state=DISABLED)


if __name__ == '__main__':
    SeriaController()

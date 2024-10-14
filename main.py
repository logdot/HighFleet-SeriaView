from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext, ttk
import seria

__author__ = 'Max'
__version__ = '0.1.0'

_TIP_FILE = 'Open a file to view details'
_TIP_NODE = 'Click on an item to view details'


class SeriaController:
    def __init__(self):
        self.root = Tk()
        self.root.title(f'SeriaView v{__version__}')
        self.root.geometry('640x480')
        self.root.minsize(640, 480)

        # Data model
        self.var_viewmode = IntVar(value=0)
        self.var_filepath: str = StringVar()
        self.seria: seria.SeriaNode = None
        # reference to seria node, easy to modify
        self.ammo_nodes = list()
        self.squadron_nodes = list()

        # Base view
        self.frm_baseview: Frame = None
        self.tree_ammo: ttk.Treeview = None
        self.tree_squadron: ttk.Treeview = None

        # TODO Map view
        # self.frm_map: Frame = None

        # Tree view
        self.frm_treeview: Frame = None
        self.tree_seria: ttk.Treeview = None
        self.text_treeview_detail: scrolledtext.ScrolledText = None

        self._make_menu()
        self._make_baseview()
        self._make_treeview()
        # TODO make map view
        self._on_view_change()

        self.root.mainloop()

    def _make_menu(self):
        def show_about():
            messagebox.showinfo(
                'About', f'''SeriaView v{__version__}
Developed by {__author__}
More information at: https://github.com/DKAMX/HighFleet-SeriaView''')

        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        menu_file = Menu(menubar, tearoff=False)
        menu_file.add_command(label='Open', command=self.open_file)
        menu_file.add_command(label='Save', command=self.save_file)
        menu_file.add_command(label='Close', command=self.close_file)
        menubar.add_cascade(label='File', menu=menu_file)

        menu_view = Menu(menubar, tearoff=False)
        menu_view.add_radiobutton(label='Base view', command=self._on_view_change,
                                  value=0, variable=self.var_viewmode)
        # menu_view.add_radiobutton(label='Map view', command=self._on_view_change,
        #                           value=1, variable=self.view_mode)
        menu_view.add_radiobutton(label='Tree view', command=self._on_view_change,
                                  value=2, variable=self.var_viewmode)
        menubar.add_cascade(label='View', menu=menu_view)

        menubar.add_command(label='About', command=show_about)

    def _on_view_change(self):
        if self.var_viewmode.get() == 0:
            self.frm_baseview.pack(expand=True, fill=BOTH)
            # self.frm_map.pack_forget()
            self.frm_treeview.pack_forget()
        elif self.var_viewmode.get() == 1:
            pass
            # TODO
            # self.frm_base.pack_forget()
            # self.frm_map.pack(expand=True, fill=BOTH)
            # self.frm_tree.pack_forget()
        elif self.var_viewmode.get() == 2:
            self.frm_baseview.pack_forget()
            # self.frm_map.pack_forget()
            self.frm_treeview.pack(expand=True, fill=BOTH)

    def _make_baseview(self):
        self.frm_baseview = Frame(self.root)
        self.frm_baseview.columnconfigure(0, weight=1)
        self.frm_baseview.columnconfigure(1, weight=1)
        self.frm_baseview.rowconfigure(0, weight=2)
        self.frm_baseview.rowconfigure(1, weight=1)

        # special ammunition register panel
        frm_ammo = LabelFrame(self.frm_baseview, text='Ammunition')
        frm_ammo.grid(row=0, column=0, sticky=NSEW)
        frm_ammo.propagate(False)

        self.tree_ammo = ttk.Treeview(frm_ammo, columns=['type', 'count'],
                                      selectmode=BROWSE)
        self.tree_ammo.heading('#0', text='')
        self.tree_ammo.heading('type', anchor=CENTER, text='TYPE')
        self.tree_ammo.heading('count', anchor=CENTER, text='PCS')
        self.tree_ammo.column('#0', width=0, stretch=NO)
        self.tree_ammo.column('type', width=200)
        self.tree_ammo.column('count', anchor=CENTER, width=50)
        self.tree_ammo.pack(expand=True, fill=BOTH, side=LEFT)

        sb_ammo = ttk.Scrollbar(frm_ammo, orient='vertical',
                                command=self.tree_ammo.yview)
        sb_ammo.pack(fill=Y, side=RIGHT)
        self.tree_ammo.config(yscrollcommand=sb_ammo.set)

        # player's squadron panel
        frm_squadron = LabelFrame(self.frm_baseview, text='Squadron')
        frm_squadron.grid(row=0, column=1, sticky=NSEW)
        frm_squadron.propagate(False)

        self.tree_squadron = ttk.Treeview(frm_squadron, selectmode=BROWSE,
                                          show='tree')
        self.tree_squadron.pack(expand=True, fill=BOTH, side=LEFT)

        sb_squadron = ttk.Scrollbar(frm_squadron, orient='vertical',
                                    command=self.tree_squadron.yview)
        sb_squadron.pack(fill=Y, side=RIGHT)
        self.tree_squadron.config(yscrollcommand=sb_squadron.set)

        # control panel
        frm_control = Frame(self.frm_baseview)
        frm_control.grid(row=1, column=0, columnspan=2, sticky=NSEW)

        btn_ammo_add_100 = Button(frm_control, text='Add 100 rounds',
                                  command=self._add_ammo_100)
        btn_ammo_add_100.pack(side=LEFT)
        btn_ammo_add_500 = Button(frm_control, text='Add 500 rounds',
                                  command=self._add_ammo_500)
        btn_ammo_add_500.pack(side=LEFT)

    def _update_baseview(self):
        self._update_ammo_tree()

        for squadron in self.squadron_nodes:
            name = squadron.get_attribute('m_name')
            tree_id = self.tree_squadron.insert('', 'end', text=name)
            ships = squadron.filter_nodes(lambda n: n.header == 'm_children=7')
            for ship in ships:
                ship_name = ship.get_attribute('m_name')
                self.tree_squadron.insert(tree_id, 'end', text=ship_name)

    def _update_ammo_tree(self):
        ammo_types = {
            '8': '122mm Unguided rocket',
            '13': '340mm Unguided rocket',
            '14': '37mm Incendiary',
            '15': '57mm Incendiary',
            '16': '100mm Armor piercing',
            '17': '100mm Proximity fuze',
            '18': '100mm Incendiary',
            '19': '130mm Armor piercing',
            '20': '130mm Proximity fuze',
            '21': '130mm Incendiary',
            '22': '130mm Laser guided',
            '23': '180mm Armor piercing',
            '24': '180mm Proximity fuze',
            '25': '180mm Incendiary',
            '26': '180mm Laser guided',
            '27': '220mm Incendiary',
            '28': '300mm Incendiary',
            '30': '100 kg General purpose bomb',
            '31': '250 kg General purpose bomb',
            '35': 'Air-to-air missile'
        }

        self.tree_ammo.delete(*self.tree_ammo.get_children())

        node_index = 0
        for ammo in self.ammo_nodes:
            index = ammo.get_attribute('m_index')
            if index in ammo_types:
                # explicit set iid so it can be reused
                self.tree_ammo.insert('', 'end', iid=node_index, values=(
                    ammo_types[index], ammo.get_attribute('m_count')))
                node_index += 1

    def _add_ammo(self, amount: int):
        # will always return str regardless of initial iid type
        index = self.tree_ammo.focus()

        if index == '':
            return

        ammo = self.ammo_nodes[int(index)]
        ammo_count = int(ammo.get_attribute('m_count'))
        ammo.set_attribute('m_count', str(ammo_count + amount))

        self._update_ammo_tree()

    def _add_ammo_100(self):
        self._add_ammo(100)

    def _add_ammo_500(self):
        self._add_ammo(500)

    def _make_treeview(self):
        self.frm_treeview = Frame(self.root)
        self.frm_treeview.columnconfigure(0, weight=1)
        self.frm_treeview.columnconfigure(1, weight=1)
        self.frm_treeview.rowconfigure(0, weight=1)

        # seria tree panel
        frm_tree = Frame(self.frm_treeview)
        frm_tree.grid(row=0, column=0, sticky=NSEW)
        frm_tree.propagate(False)

        self.tree_seria = ttk.Treeview(frm_tree, selectmode=BROWSE,
                                       show='tree')
        self.tree_seria.pack(expand=True, fill=BOTH, side=LEFT)

        sb_tree = ttk.Scrollbar(frm_tree, orient='vertical',
                                command=self.tree_seria.yview)
        sb_tree.pack(fill=Y, side=RIGHT)
        self.tree_seria.config(yscrollcommand=sb_tree.set)

        # seria node detail panel
        frm_detail = Frame(self.frm_treeview)
        frm_detail.grid(row=0, column=1, sticky=NSEW)
        frm_detail.propagate(False)

        self.text_treeview_detail = scrolledtext.ScrolledText(
            frm_detail, width=40)
        self.text_treeview_detail.insert('end', _TIP_FILE)
        self.text_treeview_detail.config(state=DISABLED)
        self.text_treeview_detail.pack(expand=True, fill=BOTH)

        self.tree_seria.bind('<<TreeviewSelect>>', self._on_tree_seria_select)

    def _update_treeview(self):
        def get_node_summary(node: seria.SeriaNode):
            classname = node.get_attribute('m_classname')
            name = node.get_attribute('m_name')
            codename = node.get_attribute('m_codename')
            fullname = node.get_attribute('m_fullname')
            code = node.get_attribute('m_code')
            if classname == 'Escadra':
                return f'Squadron {name}'
            elif classname == 'Location':
                return f'City {name} ({codename})'
            elif classname == 'NPC':
                return f'{classname} {fullname}' if str.isalpha(name) and fullname else classname
            elif classname == 'Node':
                return f'{classname} {name}' if code == '7' else classname
            elif classname == 'Body':
                return f'{classname} {name}' if name else classname
            return classname

        def append_children(node: seria.SeriaNode, parent_id: str):
            node_id = self.tree_seria.insert(
                parent_id, 'end', text=get_node_summary(node))
            for child in node.get_nodes():
                append_children(child, node_id)

        self.tree_seria.delete(*self.tree_seria.get_children())

        # populate tree with seria nodes
        root_id = self.tree_seria.insert(
            '', 'end', text=get_node_summary(self.seria))

        for node in self.seria.get_nodes():
            append_children(node, root_id)

        self.tree_seria.item(root_id, open=True)

        self.text_treeview_detail.config(state=NORMAL)
        self.text_treeview_detail.delete(1.0, END)
        self.text_treeview_detail.insert(
            'end', _TIP_NODE)
        self.text_treeview_detail.config(state=DISABLED)

    def _on_tree_seria_select(self, event):
        def print_key_value(k, v):
            return f'{k}: {v}\n' if not k.startswith('_') else f'{v}\n'

        def print_node_attributes(node: seria.SeriaNode):
            self.text_treeview_detail.config(state=NORMAL)
            self.text_treeview_detail.delete(1.0, END)
            for key, value in node.get_attributes().items():
                if isinstance(value, list):
                    for v in value:
                        self.text_treeview_detail.insert(
                            'end', print_key_value(key, v))
                else:
                    self.text_treeview_detail.insert(
                        'end', print_key_value(key, value))
            self.text_treeview_detail.config(state=DISABLED)

        node_id = event.widget.focus()
        parent_id = self.tree_seria.parent(node_id)

        if parent_id == '':
            print_node_attributes(self.seria)
            return

        # node index sequence (from root to selected node)
        index_sequence = []
        while parent_id != '':
            index_sequence.insert(0, self.tree_seria.index(node_id))
            node_id = parent_id
            parent_id = self.tree_seria.parent(node_id)

        node = self.seria
        for index in index_sequence:
            node = node.get_node(index)

        print_node_attributes(node)

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[('Seria files', '*.seria')])

        if file_path:
            self.var_filepath = file_path
            self.seria = seria.load(file_path)

            self.ammo_nodes = self.seria.get_nodes_by_class('Item')
            self.squadron_nodes = self.seria.filter_nodes(
                lambda n: n.header == 'm_escadras=327' and n.get_attribute('m_name') in {'MARK', 'DETACHMENT'})

            self._update_baseview()
            self._update_treeview()

            self.root.title(f'SeriaView v{__version__} - {file_path}')

    def save_file(self):
        if self.seria is None:
            return

        filepath = filedialog.asksaveasfilename(
            filetypes=[('Seria files', '*.seria')])

        if filepath:
            seria.dump(self.seria, filepath)
            messagebox.showinfo('Save', f'File saved to: {filepath}')

    def close_file(self):
        self.seria = None

        # clear base view
        self.tree_ammo.delete(*self.tree_ammo.get_children())
        self.tree_squadron.delete(*self.tree_squadron.get_children())

        # clear tree view
        self.tree_seria.delete(*self.tree_seria.get_children())
        self.text_treeview_detail.config(state=NORMAL)
        self.text_treeview_detail.delete(1.0, END)
        self.text_treeview_detail.insert('end', _TIP_FILE)
        self.text_treeview_detail.config(state=DISABLED)

        self.root.title(f'SeriaView v{__version__}')


if __name__ == '__main__':
    SeriaController()

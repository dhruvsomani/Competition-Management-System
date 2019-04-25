import tkinter
import tkinter.ttk
import tkinter.tix

class EditableTreeview(tkinter.ttk.Treeview):
    def __init__(self, *args, **kwargs):
        tkinter.ttk.Treeview.__init__(self, selectmode=tkinter.NONE, *args, **kwargs)
        self.widget = kwargs.pop('widget', tkinter.Entry(font=('Arial', 12)))

        # self.bind('<Button-1>', self.callback)
        self.bind('<Double-Button-1>', self.edit_row)
        self.bind('<Button-3>', self.edit_row)


    def edit_row(self, event):
        if self.identify_region(event.x, event.y) == 'cell':
            selected_item = self.focus()

            column = int(self.identify_column(event.x)[1:])-1
            row = self.item(selected_item)

            if column >= 2:
                self.widget.delete(0, tkinter.END)
                self.widget.insert(tkinter.END, row['values'][column])
                self.widget.place(x=event.x+self.winfo_rootx(), y=event.y+80)
                self.widget.focus_set()
                self.widget.select_range(0, tkinter.END)

                # self.widget.bind('<Enter>', lambda event: self.update_data(self.widget, row, column))
                # self.widget.bind('<Return>', lambda event: self.update_data(self.widget, row, column))
                self.widget.bind('<Leave>', lambda event: self.update_data(self.widget, row['values'][0], column))


    def update_data(self, widget, row, column):
        self.event_generate('<<EditableTreeviewEdited>>', when='tail', x=column, y=row)
        widget.place_forget()


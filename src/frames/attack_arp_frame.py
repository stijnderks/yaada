import tkinter as tk
import discovery as dis
import netifaces
from tkinter import messagebox


class AttackARPFrame(tk.Frame):

    def __init__(self, parent, controller):
        """
        Initialises GUI of the frame used for selecting the target
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#DADADA')

        top_frame = tk.Frame(self)
        top_frame.configure(bg='#DADADA')

        label_frame = tk.Frame(self, height=15)
        label_frame.configure(bg='#DADADA')

        button_set_frame = tk.Frame(self, height=15)
        button_set_frame.configure(bg='#DADADA')

        bottom_frame = tk.Frame(self)
        bottom_frame.configure(bg='#DADADA')

        top_frame.pack(side="top", fill="x")
        button_set_frame.pack(side="top", fill="both", expand=True)
        bottom_frame.pack(side="bottom", fill="both", expand=True)
        label_frame.pack(side="bottom", fill="both", expand=True)

        self.label_ip = tk.Label(top_frame, text="Gateway to use (already provided is default)",
                                 font=(self.controller.font, self.controller.font_size))
        self.label_ip.config(bg='#DADADA', fg='black')
        self.label_ip.pack(side='top', pady=5)

        self.textbox_ip = tk.Entry(top_frame, width=20, font=(self.controller.font, self.controller.font_size),
                                   justify='center')
        self.textbox_ip.insert(0, self.get_local_ip())
        self.textbox_ip.pack(side='top', pady=5)

        # TODO: Display more information about ip address/mac address?
        # See: https://www.studytonight.com/network-programming-in-python/integrating-port-scanner-with-nmap
        self.button_scan = tk.Button(top_frame, text="Scan", command=self.update_local, width=30,
                                     font=(self.controller.font, self.controller.font_size))
        self.button_scan.config(bg='#DADADA', fg='black')
        self.button_scan.pack(side='top', pady=5)

        self.ip_box = tk.Listbox(top_frame, width=45, selectmode=tk.SINGLE,
                                 font=(self.controller.font, self.controller.font_size), justify='center', activestyle='none')
        self.ip_box.pack(side='top', pady=10)

        self.button_victim = tk.Button(button_set_frame, text="Set victim", command=self.set_victim, width=15,
                                       font=(self.controller.font, self.controller.font_size))
        self.button_victim.config(bg='#DADADA', fg='black')
        self.button_victim.place(relx=0.30, rely=0.5, anchor=tk.CENTER)

        self.button_target = tk.Button(button_set_frame, text="Set target", command=self.set_target, width=15,
                                       font=(self.controller.font, self.controller.font_size))
        self.button_target.config(bg='#DADADA', fg='black')
        self.button_target.place(relx=0.70, rely=0.5, anchor=tk.CENTER)

        self.label_victim = tk.Label(label_frame, text="Victim: None", font=(self.controller.font,
                                                                             self.controller.font_size))
        self.label_victim.config(bg='#DADADA', fg='black')
        self.label_victim.place(relx=0.30, rely=0.5, anchor=tk.CENTER)

        self.label_target = tk.Label(label_frame, text="Target: None", font=(self.controller.font,
                                                                             self.controller.font_size))
        self.label_target.config(bg='#DADADA', fg='black')
        self.label_target.place(relx=0.70, rely=0.5, anchor=tk.CENTER)

        self.button_start = tk.Button(bottom_frame, text="Start spoofing", command=self.start_arp, width=15,
                                      font=(self.controller.font, self.controller.font_size))
        self.button_start.config(bg='#DADADA', fg='black')
        self.button_start.pack(side='top', pady=10)
        self.button_start.config(state=tk.DISABLED)

        self.button_stop = tk.Button(bottom_frame, text="Stop spoofing", command=self.stop_arp, width=15,
                                     font=(self.controller.font, self.controller.font_size))
        self.button_stop.config(bg='#DADADA', fg='black')
        self.button_stop.pack(side='top')
        self.button_stop.config(state=tk.DISABLED)

    def update_local(self):
        # TODO: check if address is a valid IP. Otherwise, raise warning
        address = self.textbox_ip.get()

        self.ip_box.delete(0, tk.END)
        self.controller.log.update_stat('Searching for local network addresses')
        self.controller.log.update_out('searching for local network addresses')

        options = dis.arp_ping(netmask=address)
        if not len(options) == 0:
            for option in options:
                # TODO: Add "(self)" behind own MAC-ip address combo so that the user knows their own address
                self.ip_box.insert(tk.END, option)
        else:
            self.ip_box.insert(tk.END, "could not find any IP addresses")
            self.controller.log.update_out('could not find any IP addresses')

        self.controller.log.update_stat('Finished searching for local network addresses')
        self.controller.log.update_out('finished searching for local network addresses')

    @staticmethod
    def get_local_ip():
        # TODO: Text escaping/converting to host model, and adding (default) behind the text?
        gws = netifaces.gateways()
        return str(gws['default'][netifaces.AF_INET][0]) + '/24'

    def set_target(self):
        # TODO: Extend to MULTIPLE rather than SINGLE
        try:
            target = self.ip_box.get(self.ip_box.curselection())
            self.ip_box.select_clear(0, tk.END)
            target = str(target).split('at ', 1)[1]
            self.controller.log.update_out(target + ' has been set as the target IP address')
            self.label_target.config(text=('Target: ' + target))
            self.enable_start()
        except tk.TclError:
            self.dis_err('target')

    def set_victim(self):
        try:
            victim = self.ip_box.get(self.ip_box.curselection())
            self.ip_box.select_clear(0, tk.END)
            victim = str(victim).split('at ', 1)[1]
            self.controller.log.update_out(victim + ' has been set as the victim IP address')
            self.label_victim.config(text=('Victim: ' + victim))
            self.enable_start()
        except tk.TclError:
            self.dis_err('victim')

    def enable_start(self):
        victim_text = self.label_victim.cget('text')
        target_text = self.label_target.cget('text')

        if (victim_text != 'Victim: None') and (target_text != 'Target: None'):
            self.button_start.config(state=tk.NORMAL)
            self.controller.log.update_out('both victim and target set have been set')
            self.controller.log.update_out('ready for action')

    def start_arp(self):
        # TODO: implement in arp_attack.py (?)
        self.button_stop.config(state=tk.NORMAL)
        self.button_start.config(state=tk.DISABLED)

        self.controller.log.update_out('starting ARP spoofing')
        self.controller.log.update_stat('ARP spoofing is active')
        return

    def stop_arp(self):
        # TODO: implement in arp_attack.py (?)
        self.button_start.config(state=tk.NORMAL)
        self.button_stop.config(state=tk.DISABLED)

        self.controller.log.update_out('stopping ARP spoofing')
        self.controller.log.update_stat('ARP spoofing is inactive')
        return

    @staticmethod
    def dis_err(case):
        """
        Displays a message box containing error
        """
        messagebox.showerror("Error", "Please make sure to first select a " + case + " IP before pressing the button.")

class GuidePlotPanel(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        super(GuidePlotPanel, self).__init__(parent)
        self.parent = parent
        self.data1 = []
        self.data2 = [] 
        
        self.__DoLayout()

    def __DoLayout(self):
        self.init_plot()
        self.canvas = FigCanvas(self, -1, self.fig)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.SetSizer(self.vbox)
        self.vbox.Fit(self)
        #self.SetBackgroundColour(panelcolor)

        #subscribe to xy updates
        pub.subscribe(self.data_update, "shiftupdate")

      
    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((2.0, 2.0), dpi=self.dpi, facecolor='0.9')
        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title(r'Guiding Corrections: cyan + $\rightarrow$ x magenta * $\rightarrow$ y', size=8)
        self.axes.set_ylabel('Pixels', size=8)
        self.axes.set_xlabel('Seconds', size=8)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=6)
        pylab.setp(self.axes.get_yticklabels(), fontsize=6)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        self.plot_data1 = self.axes.plot(self.data1, 'c+')[0]
        self.plot_data2 = self.axes.plot(self.data2, 'm*')[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        xmax = len(self.data1) if len(self.data1) > 50 else 50
        xmin = xmax - 50
        
        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        ymin = round(min(min(self.data1),min(self.data2)), 0) - 0.5
        ymax = round(max(max(self.data1),max(self.data2)), 0) + 0.5
        
        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        self.axes.grid(True, color='gray')
        #self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axes.get_xticklabels(), 
            visible=True)
        
        self.plot_data1.set_xdata(np.arange(len(self.data1)))
        self.plot_data1.set_ydata(np.array(self.data1))
        self.plot_data2.set_xdata(np.arange(len(self.data2)))
        self.plot_data2.set_ydata(np.array(self.data2))
        
        self.canvas.draw()
    
    def data_update(self, msg):
        print "xshift: ", msg.data[0][0], " yshift: ", msg.data[0][1]
        #add new data
        self.data1.append(msg.data[0][0])
        self.data2.append(msg.data[0][1])
        
        self.draw_plot()
        
    def data_clear(self):
        self.data1 = [0]
        self.data2 = [0]
        self.draw_plot()
        

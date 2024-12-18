import matplotlib.pyplot as plt

class SessionPlotManager:
    def __init__(self):
        self.current_figure = None
        
    def create_session_plot(self, sessions_by_date):
        if self.current_figure:
            plt.close(self.current_figure)
            
        self.current_figure = plt.figure(figsize=(10, 6))
        ax = self.current_figure.add_subplot(111)
        
        x_positions = []
        heights = []
        x_labels = []
        
        for i, (date, sessions) in enumerate(sessions_by_date.items()):
            for j, (start_time, duration) in enumerate(sessions):
                x_positions.append(i + j * 0.2)
                heights.append(duration)
                x_labels.append(f"{date}\n{start_time}")
        
        bars = ax.bar(x_positions, heights, width=0.15)
        
        self._customize_plot(ax, x_positions, x_labels, bars)
        plt.tight_layout()
        
        return self.current_figure
        
    def _customize_plot(self, ax, x_positions, x_labels, bars):
        ax.set_title('Individual Sessions by Day')
        ax.set_xlabel('Date and Start Time')
        ax.set_ylabel('Duration (minutes)')
        
        plt.xticks(x_positions, x_labels, rotation=45, ha='right')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}m',
                   ha='center', va='bottom')
                   
    def cleanup(self):
        if self.current_figure:
            plt.close(self.current_figure) 
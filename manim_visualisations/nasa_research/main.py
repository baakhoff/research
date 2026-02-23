from manim import *
import pandas as pd
import os
import sys

class abs_mag_distribution(Scene):
    def construct(self):
        try:
            # Fix: Use absolute path relative to this script
            script_dir = os.path.dirname(__file__)
            csv_path = os.path.join(script_dir, '../../data/nasa_data/all_neos.csv')
            all_neos_df = pd.read_csv(csv_path)
            
            stats = all_neos_df['absolute_magnitude_h'].dropna()
            
            # Calculate distribution (histogram) showing count for each magnitude (rounded)
            distribution = stats.round(0).value_counts().sort_index()
            names = [str(int(val)) for val in distribution.index]
            counts = distribution.values.tolist()
            
            y_max = max(counts) if counts else 1
            y_step = max(1, int(y_max // 5))
            
            # Create chart
            chart = BarChart(
                values=counts,
                bar_names=names,
                y_range=[0, y_max * 1.1, y_step],
                y_length=6,
                x_length=10,
                x_axis_config={"font_size": 24},
            )
            
            # Explicitly replace default Tex labels with Text labels using the custom font
            new_x_labels = VGroup(*[Text(name, font_size=15, font="Momo Trust Display") for name in names])
            for old_lbl, new_lbl in zip(chart.x_axis.labels, new_x_labels):
                new_lbl.move_to(old_lbl)
            chart.x_axis.labels.become(new_x_labels)

            new_y_labels = VGroup() 
            for num in chart.y_axis.numbers:
                # Use get_value() if it's a DecimalNumber, otherwise use its string representation
                val = int(round(num.get_value())) if hasattr(num, 'get_value') else num.tex_strings[0]
                new_lbl = Text(str(val), font_size=15, font="Momo Trust Display")
                new_lbl.move_to(num)
                new_y_labels.add(new_lbl)
            chart.y_axis.numbers.become(new_y_labels)
            
            # Add labels on top of each bar
            bar_labels = VGroup()
            for bar, count in zip(chart.bars, counts):
                label = Text(str(int(count)), font_size=14, font="Momo Trust Display")
                label.rotate(PI / 2)  # 90 degrees counterclockwise
                label.next_to(bar, UP, buff=0.15)
                bar_labels.add(label)
            
            # Added to chart so it scales and animates along with it
            chart.add(bar_labels)
            
            # Axis labels
            x_label = Text("Magnitude", font_size=24, font="Momo Trust Display")
            y_label = Text("Number of Asteroids", font_size=24, font="Momo Trust Display")
            x_label.next_to(chart.x_axis, DOWN, buff=0.4)
            y_label.rotate(PI / 2)
            y_label.next_to(chart.y_axis, LEFT, buff=0.5)
            chart.add(x_label, y_label)

            # Scale chart to fit nicely on screen
            chart.scale(0.8)
            chart.shift(DOWN * 0.5)

            # # Title
            title = VGroup(
                Text("Distribution of Absolute Magnitude", font_size=36, font='Momo Trust Display'),
                Text("of Near Earth Objects", font_size=36, font='Momo Trust Display')
            ).arrange(DOWN, buff=0.1)
            title.to_edge(UP)

            self.play(Create(chart))
            self.play(Write(title))
            self.wait(2)
        except Exception as e:
            print(f"Error: {e}")
            text = Text(f"Error: {str(e)}", font_size=24, color=RED)
            self.add(text)
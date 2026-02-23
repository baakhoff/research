from manim import *
import pandas as pd
import os
import sys
import json

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

class hazardous_size_distribution(Scene):
    def _make_chart(self, all_neos_df, is_hazardous):
        bins = [0, 100, 500, 1000, 2000, 5000, 10000, 25000, 50000, 100000, float('inf')]
        labels = ['0-100', '100-500', '500-1K', '1K-2K', '2K-5K', '5K-10K', '10K-25K', '25K-50K', '50K-100K', '100K+']

        stats = all_neos_df[all_neos_df['is_potentially_hazardous_asteroid'] == is_hazardous]['estimated_diameter_meters_max'].dropna()
        binned = pd.cut(stats, bins=bins, labels=labels)
        distribution = binned.value_counts().sort_index()
        names = [str(label) for label in distribution.index]
        counts = distribution.values.tolist()

        y_max = max(counts) if counts else 1
        y_step = max(1, int(y_max // 5))

        chart = BarChart(
            values=counts,
            bar_names=names,
            y_range=[0, y_max * 1.1, y_step],
            y_length=3.5,
            x_length=10,
            x_axis_config={"font_size": 24},
        )

        # Replace x-axis labels with custom font
        new_x_labels = VGroup(*[Text(name, font_size=12, font="Momo Trust Display") for name in names])
        for old_lbl, new_lbl in zip(chart.x_axis.labels, new_x_labels):
            new_lbl.move_to(old_lbl)
        chart.x_axis.labels.become(new_x_labels)

        # Replace y-axis labels with custom font
        new_y_labels = VGroup()
        for num in chart.y_axis.numbers:
            val = int(round(num.get_value())) if hasattr(num, 'get_value') else num.tex_strings[0]
            new_lbl = Text(str(val), font_size=12, font="Momo Trust Display")
            new_lbl.move_to(num)
            new_y_labels.add(new_lbl)
        chart.y_axis.numbers.become(new_y_labels)

        # Bar value labels
        bar_labels = VGroup()
        for bar, count in zip(chart.bars, counts):
            label = Text(str(int(count)), font_size=11, font="Momo Trust Display")
            label.rotate(PI / 2)
            label.next_to(bar, UP, buff=0.1)
            bar_labels.add(label)
        chart.add(bar_labels)

        # Axis labels
        x_label = Text("Size (meters)", font_size=18, font="Momo Trust Display")
        y_label = Text("Count", font_size=18, font="Momo Trust Display")
        x_label.next_to(chart.x_axis, DOWN, buff=0.3)
        y_label.rotate(PI / 2)
        y_label.next_to(chart.y_axis, LEFT, buff=0.4)
        chart.add(x_label, y_label)

        return chart

    def construct(self):
        try:
            script_dir = os.path.dirname(__file__)
            csv_path = os.path.join(script_dir, '../../data/nasa_data/all_neos.csv')
            all_neos_df = pd.read_csv(csv_path)
            all_neos_df['estimated_diameter_meters_max'] = all_neos_df.estimated_diameter.apply(
                lambda x: round(json.loads(x.replace("'", '"'))['kilometers']['estimated_diameter_max'] * 1000, 2)
                if isinstance(x, str) else None
            )

            # --- Top chart: Hazardous ---
            chart_haz = self._make_chart(all_neos_df, True)
            chart_haz.scale(0.65)
            chart_haz.move_to(DOWN * 2.5)

            subtitle_haz = Text("Hazardous", font_size=18, font="Momo Trust Display", color=RED)
            subtitle_haz.next_to(chart_haz, UP, buff=0.15)

            # --- Bottom chart: Non-hazardous ---
            chart_safe = self._make_chart(all_neos_df, False)
            chart_safe.scale(0.65)
            chart_safe.move_to(UP * 1.3)

            subtitle_safe = Text("Not Hazardous", font_size=18, font="Momo Trust Display", color=GREEN)
            subtitle_safe.next_to(chart_safe, UP, buff=0.15)

            # --- Main title ---
            title = Text("Distribution of Asteroid Size by Hazard Status", font_size=30, font='Momo Trust Display')
            title.to_edge(UP, buff=0.2)

            self.play(Write(title))
            self.play(Create(chart_haz), Write(subtitle_haz))
            self.play(Create(chart_safe), Write(subtitle_safe))
            self.wait(2)
        except Exception as e:
            print(f"Error: {e}")
            text = Text(f"Error: {str(e)}", font_size=24, color=RED)
            self.add(text)
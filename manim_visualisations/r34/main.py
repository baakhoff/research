from manim import *
import pandas as pd
import os
import sys

class TopTagsByCharacter(Scene):
    def construct(self):
        try:
            df = pd.read_csv('data/r34data/rule34_tags.csv')
            
            df_most_posts_by_character = df[df['type']=='Character'].sort_values(by='count', ascending=False).head(30)

            names = [
                name.replace("&", "\\&")
                    .replace("%", "\\%")
                    .replace("$", "\\$")
                    .replace("#", "\\#")
                    .replace("_", "\\_") 
                for name in df_most_posts_by_character['name'].tolist()
            ]
            counts = df_most_posts_by_character['count'].tolist()


            # Create chart
            chart = BarChart(
                values=counts,
                bar_names=names,
                y_range=[0, max(counts) * 1.1, max(counts) // 5],
                y_length=10,
                x_length=5,
                x_axis_config={"font_size": 24},
            )

            chart.rotate(-PI / 2)

            # Rotate y-axis numbers
            for label in chart.y_axis.numbers:
                label.rotate(PI / 2, about_point=label.get_center())
                label.align_to(chart.y_axis, DOWN)
                label.shift(UP * 0.4)

            # # Rotate x-axis labels to avoid overlap
            # # Accessing the labels grouping
            for label in chart.x_axis.labels:
                label.rotate(PI / 2, about_point=label.get_center())
                label.scale(0.6)
                label.align_to(chart.x_axis, RIGHT)
                label.shift(LEFT * 0.5)

            chart.shift (RIGHT * 0.7)
            

            # # Title
            title = Text("Top 50 Rule34 Tags", font_size=36)
            title.to_edge(UP)

            self.play(Create(chart))
            self.play(Write(title))
            self.wait(2)
        except Exception as e:
            print(f"Error: {e}")
            text = Text(f"Error: {str(e)}", font_size=24, color=RED)
            self.add(text)

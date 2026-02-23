from manim import *
import pandas as pd
import os
import sys
import json

script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir, '../../data/nasa_data/all_neos.csv')
all_neos_df = pd.read_csv(csv_path)

all_neos_df['estimated_diameter_meters_max'] = all_neos_df.estimated_diameter.apply(
    lambda x: round(json.loads(x.replace("'", '"'))['kilometers']['estimated_diameter_max'] * 1000, 2)
    if isinstance(x, str) else None
)

all_neos_df['close_approach_data_parsed'] = (
    all_neos_df['close_approach_data']
    .str.replace("'", '"', regex=False)
    .apply(json.loads)
)

exploded_df = all_neos_df.explode('close_approach_data_parsed')

cad_normalized = pd.json_normalize(exploded_df['close_approach_data_parsed'])
cad_normalized

cad_normalized.index = exploded_df.index

cad_normalized['relative_velocity_kph'] = pd.to_numeric(
    cad_normalized['relative_velocity.kilometers_per_hour'])
cad_normalized['miss_distance_meters'] = pd.to_numeric(
    cad_normalized['miss_distance.kilometers']) * 1000

child_cols = ['close_approach_date','close_approach_date_full',
            'orbiting_body',
            'relative_velocity_kph', 'miss_distance_meters']
final_child_data = cad_normalized[child_cols]

parent_cols = [
    'neo_reference_id', 'id', 'name', 'absolute_magnitude_h',
    'is_sentry_object', 'estimated_diameter_meters_max',
    'is_potentially_hazardous_asteroid'
]

close_approach_data = final_child_data.join(all_neos_df[parent_cols])

# Reset index for a clean final dataframe
close_approach_data.reset_index(drop=True, inplace=True)
close_approach_data.head()


class abs_mag_distribution(Scene):
    def construct(self):
        try:
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
                label = Text(str(int(count)), font_size=14, font="Momo Trust Display", disable_ligatures=True)
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
            label = Text(str(int(count)), font_size=11, font="Momo Trust Display", disable_ligatures=True)
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

class orbiting_body_distribution(Scene):
    def construct(self):
        try:
            stats = close_approach_data.groupby('orbiting_body')['neo_reference_id'].nunique().sort_index()
            
            names = [str(val) for val in stats.index]
            counts = stats.values.tolist()
            
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
                label = Text(str(int(count)), font_size=14, font="Arial", disable_ligatures=True)
                #label.rotate(PI / 2)  # 90 degrees counterclockwise
                label.next_to(bar, UP, buff=0.15)
                bar_labels.add(label)
            
            # Added to chart so it scales and animates along with it
            chart.add(bar_labels)
            
            # Axis labels
            x_label = Text("Orbiting Body", font_size=24, font="Momo Trust Display")
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
                Text("Distribution of Orbiting Body", font_size=36, font='Momo Trust Display'),
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

class orbiting_body_hazardous(Scene):
    def construct(self):
        try:
            # ── Data ──────────────────────────────────────────────────────────
            raw = (
                close_approach_data
                .groupby(['orbiting_body', 'is_potentially_hazardous_asteroid'])['neo_reference_id']
                .nunique()
                .unstack(fill_value=0)
            )
            pct = raw.div(raw.sum(axis=1), axis=0) * 100
            bodies = pct.index.tolist()
            haz_pct  = [float(pct.loc[b, True])  if True  in pct.columns else 0.0 for b in bodies]
            safe_pct = [float(pct.loc[b, False]) if False in pct.columns else 0.0 for b in bodies]

            # ── Layout constants ──────────────────────────────────────────────
            n          = len(bodies)
            chart_h    = 4.8          # height = 100 %
            chart_bot  = -2.6
            bar_w      = min(0.65, 8.5 / n - 0.12)
            gap        = 0.12
            total_w    = n * (bar_w + gap) - gap
            x_offset   = -total_w / 2  # left edge of first bar
            axis_x     = x_offset - 0.35

            HAZ_COLOR  = "#E53935"
            SAFE_COLOR = "#43A047"
            FONT       = "Momo Trust Display"

            # ── Bars ──────────────────────────────────────────────────────────
            bars_group   = VGroup()
            xlbls_group  = VGroup()
            pct_labels   = VGroup()

            for i, (body, hp, sp) in enumerate(zip(bodies, haz_pct, safe_pct)):
                cx = x_offset + i * (bar_w + gap) + bar_w / 2

                h_safe = sp / 100 * chart_h
                h_haz  = hp / 100 * chart_h

                # Safe / not-hazardous (bottom segment)
                if h_safe > 1e-3:
                    r_safe = Rectangle(
                        width=bar_w, height=h_safe,
                        fill_color=SAFE_COLOR, fill_opacity=0.9, stroke_width=0
                    ).move_to([cx, chart_bot + h_safe / 2, 0])
                    bars_group.add(r_safe)

                # Hazardous (top segment)
                if h_haz > 1e-3:
                    r_haz = Rectangle(
                        width=bar_w, height=h_haz,
                        fill_color=HAZ_COLOR, fill_opacity=0.9, stroke_width=0
                    ).move_to([cx, chart_bot + h_safe + h_haz / 2, 0])
                    bars_group.add(r_haz)

                    # % label inside hazardous segment (only if segment is tall enough)
                    if h_haz > 0.25:
                        pl = Text(f"{hp:.0f}%", font_size=10, font=FONT,
                                  disable_ligatures=True, color=WHITE)
                        pl.move_to([cx, chart_bot + h_safe + h_haz / 2, 0])
                        pct_labels.add(pl)

                # X-axis label (rotated)
                lbl = Text(body, font_size=11, font=FONT)
                lbl.rotate(-PI / 4)
                lbl.next_to([cx, chart_bot, 0], DOWN, buff=0.18)
                xlbls_group.add(lbl)

            # ── Axes ──────────────────────────────────────────────────────────
            y_axis = Line(
                [axis_x, chart_bot, 0],
                [axis_x, chart_bot + chart_h, 0],
                color=GREY
            )
            x_axis_line = Line(
                [axis_x, chart_bot, 0],
                [axis_x + total_w + bar_w, chart_bot, 0],
                color=GREY
            )

            # ── Y ticks & labels ──────────────────────────────────────────────
            ticks_group = VGroup()
            gridlines   = VGroup()
            for pv in [0, 25, 50, 75, 100]:
                y = chart_bot + pv / 100 * chart_h
                tick = Line([axis_x - 0.12, y, 0], [axis_x, y, 0], color=GREY)
                tlbl = Text(f"{pv}%", font_size=12, font=FONT)
                tlbl.next_to([axis_x - 0.12, y, 0], LEFT, buff=0.08)
                ticks_group.add(tick, tlbl)
                if pv > 0:
                    gl = DashedLine(
                        [axis_x, y, 0],
                        [axis_x + total_w + bar_w, y, 0],
                        color=GREY, stroke_opacity=0.3
                    )
                    gridlines.add(gl)

            # ── Y-axis label ──────────────────────────────────────────────────
            y_label = Text("% of Asteroids", font_size=15, font=FONT)
            y_label.rotate(PI / 2)
            y_label.next_to(y_axis, LEFT, buff=1)

            # ── Legend ────────────────────────────────────────────────────────
            def legend_item(color, label):
                box = Rectangle(width=0.25, height=0.25,
                                 fill_color=color, fill_opacity=0.9, stroke_width=0)
                txt = Text(label, font_size=16, font=FONT, disable_ligatures=True)
                return VGroup(box, txt).arrange(RIGHT, buff=0.12)

            legend = VGroup(
                legend_item(HAZ_COLOR,  "Hazardous"),
                legend_item(SAFE_COLOR, "Not Hazardous"),
            ).arrange(RIGHT, buff=0.5)

            # ── Title ─────────────────────────────────────────────────────────
            title = Text(
                "Hazardous vs Safe Asteroids by Orbiting Body",
                font_size=28, font=FONT
            )
            title.to_edge(UP, buff=0.2)
            legend.next_to(title, DOWN, buff=0.18)

            # ── Animate ───────────────────────────────────────────────────────
            self.play(Write(title), Write(legend))
            self.play(Create(y_axis), Create(x_axis_line),
                      Create(ticks_group), Create(gridlines))
            self.play(Create(bars_group), Write(xlbls_group), Write(y_label))
            self.play(Write(pct_labels))
            self.wait(2)

        except Exception as e:
            print(f"Error: {e}")
            text = Text(f"Error: {str(e)}", font_size=24, color=RED)
            self.add(text)

class neo_by_year(Scene):
    def construct(self):
        try:
            # ── Data ──────────────────────────────────────────────────────────
            close_approach_data['year'] = pd.to_datetime(
                close_approach_data['close_approach_date']
            ).dt.year
            stats = (
                close_approach_data
                .groupby('year')['neo_reference_id']
                .nunique()
                .sort_index()
            )
            years  = stats.index.tolist()
            counts = stats.values.tolist()

            FONT = "Momo Trust Display"

            # ── Axes ──────────────────────────────────────────────────────────
            x_min, x_max = years[0],  years[-1]
            y_min, y_max = 0,          max(counts) * 1.1

            ax = Axes(
                x_range=[x_min, x_max, max(1, (x_max - x_min) // 10)],
                y_range=[y_min, y_max, max(1, int(y_max // 6))],
                x_length=11,
                y_length=5.5,
                axis_config={"include_tip": False, "color": GREY},
            )

            # ── Custom tick labels ─────────────────────────────────────────────
            x_lbls = VGroup()
            step = max(1, len(years) // 10)
            for yr in years[::step]:
                pt = ax.c2p(yr, 0)
                lbl = Text(str(int(yr)), font_size=13, font=FONT)
                lbl.rotate(-PI / 4)
                lbl.next_to(pt, DOWN, buff=0.25)
                x_lbls.add(lbl)

            y_lbls = VGroup()
            y_step = max(1, int(y_max // 6))
            for v in range(0, int(y_max), y_step):
                pt = ax.c2p(x_min, v)
                lbl = Text(str(v), font_size=13, font=FONT)
                lbl.next_to(pt, LEFT, buff=0.1)
                y_lbls.add(lbl)

            # ── Line through data points ───────────────────────────────────────
            points = [ax.c2p(yr, ct) for yr, ct in zip(years, counts)]
            line = VMobject(color="#42A5F5", stroke_width=2.5)
            line.set_points_smoothly(points)



            # ── Axis labels ───────────────────────────────────────────────────
            x_label = Text("Year", font_size=18, font=FONT)
            x_label.next_to(ax.x_axis, DOWN, buff=0.9)

            y_label = Text("Unique Asteroids", font_size=18, font=FONT)
            y_label.rotate(PI / 2)
            y_label.next_to(ax.y_axis, LEFT, buff=1.1)

            # ── Title ─────────────────────────────────────────────────────────
            title = Text(
                "Unique Near-Earth Objects per Year",
                font_size=30, font=FONT
            )
            title.to_edge(UP, buff=0.25)

            # ── Animate ───────────────────────────────────────────────────────
            self.play(Write(title))
            self.play(Create(ax), Write(x_lbls), Write(y_lbls),
                      Write(x_label), Write(y_label))
            self.play(Create(line), run_time=2)
            self.wait(2)

        except Exception as e:
            print(f"Error: {e}")
            text = Text(f"Error: {str(e)}", font_size=24, color=RED)
            self.add(text)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from py_ball import player
from matplotlib.patches import Circle, Rectangle, Arc  # Used to draw court
from matplotlib.animation import FuncAnimation

# Use a different font
plt.rcParams["font.family"] = "serif"

# Set pandas options
pd.options.mode.chained_assignment = None
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# Team colors https://teamcolorcodes.com/nba-team-color-codes/
team_colors_primary = {'GS': '#006BB6', 'LAL': '#552583', 'ATL': '#e03a3e'}
team_colors_secondary = {'GS': '#FDB927', 'LAL': '#FDB927', 'ATL': '#26282A'}


# Draw the court.  Credit to http://savvastjortjoglou.com/nba-shot-sharts.html
def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


# Get the shot data using py_ball_
HEADERS = {'Connection': 'keep-alive',
           'Host': 'stats.nba.com',
           'Origin': 'http://stats.nba.com',
           'Upgrade-Insecure-Requests': '1',
           'Referer': 'stats.nba.com',
           'x-nba-stats-origin': 'stats',
           'x-nba-stats-token': 'true',
           'Accept-Language': 'en-US,en;q=0.9',
           "X-NewRelic-ID": "VQECWF5UChAHUlNTBwgBVw==",
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0'}
league_id = '00'  # NBA
player_id = '202691'  # Klay Thompson
game_id = '0021800091'  # 11/28/2018 GSW @ Bulls
season = '2018-19'  # Season
shots = player.Player(headers=HEADERS,
                      endpoint='shotchartdetail',
                      league_id=league_id,
                      player_id=player_id,
                      game_id=game_id,
                      season=season)
shot_df = pd.DataFrame(shots.data['Shot_Chart_Detail'])
Ind = shot_df.index.values
shot_df_dict = shot_df.to_dict('dict')

# Put X and Y location data into array.  Also, set colors for makes and misses
data = []
colors = []
for i in Ind:
    data.append([-1*shot_df_dict['LOC_X'][i], shot_df_dict['LOC_Y'][i]])
    if shot_df_dict['SHOT_MADE_FLAG'][i] == 0:
        colors.append(team_colors_secondary['GS'])
    else:
        colors.append(team_colors_primary['GS'])
data = np.array(data, dtype='float')
size = np.ones(data.shape[0]) * 100

# Create the figure and some empty
fig = plt.figure(figsize=(11, 8))
plt.xlim(-300, 300)
plt.ylim(-100, 500)
graph = plt.scatter([], [])

# Draw the court
draw_court(outer_lines=True)
plt.axis('off')

# Fix aspect ratio
plt.gca().set_aspect(1)

# Add some text
plt.text(-240, 385, 'KLAY THOMPSON\n14 THREE POINTERS', size=9, weight='bold')
plt.text(240, 385, 'GSW @ CHI\n11/29/18', size=9, weight='bold', ha="right")
plt.figtext(.8, 0.09, 'Data: @py_ball_  Plot: @Pavel_Vab', fontsize=8, ha="right", va="top")


# This function is called by the animation
def animate(i):
    Xloc = data[:i+1, 0]
    Yloc = data[:i+1, 1]
    graph.set_offsets(np.vstack((Xloc, Yloc)).T)
    graph.set_sizes(size)
    graph.set_facecolors(colors[:i+1])
    return graph


# This does the animation
ani = FuncAnimation(fig, animate, repeat=False, interval=500)

# Show the animation
fig.tight_layout()
plt.show()

# You need to install imagemagick to save the animation
ani.save('/home/pavelv/BasketballAnalytics/Klay-Animated/KLAY.gif', writer='imagemagick', fps=5)

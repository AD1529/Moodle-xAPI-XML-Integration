from src.MoodleArchiveAlgorithms.moodle_archive import MoodleArchive

import networkx as nx
from networkx import DiGraph
from IPython.display import Markdown, display
from networkx.drawing.nx_pydot import graphviz_layout
from matplotlib.lines import Line2D
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from pandas import DataFrame


def course_chaptering(archive: MoodleArchive):
    """
    An interactive way to select the chapter to visualise. Ticked chapters are used for representation.
    """
    heading = "Tick the sections that correspond to course chapters: "
    display(Markdown(heading))
    for section in archive.section_list:
        chapter = section.settings.is_chapter
        if chapter:
            display(chapter)


def create_course_structure(archive: MoodleArchive) -> DiGraph:
    """
    Takes a moodle archive and creates a directed graph of the course.

    Parameters
    ----------
    archive

    Returns
    -------
    A Directed Graph of the course structure.

    """
    course = DiGraph()
    course.add_node('course',
                    name_=archive.course.settings.name,
                    type_='course',
                    settings=archive.course.settings)

    idx = 0
    for section in archive.section_list:
        ss = section.settings
        if ss.is_chapter and ss.is_chapter.value:
            idx += 1
            course.add_node(f"{idx}",
                            name_=ss.name,
                            type_='chapter',
                            settings=ss
                            )
            course.add_edge("course",
                            f"{idx}",
                            )
            add_activities(course, archive, f"{idx}")

    add_chapters(course, archive, 'course')

    return course


def add_chapters(course: DiGraph, archive: MoodleArchive, level) -> DiGraph:
    """
    Takes the Directed Graph of course and adds sections to it. Since there can be many subsections, it leverages a
    recursive function to recursively add sections to the graph.

    Parameters
    ----------
    course: course id
    archive: the Moodle archive of the course
    level: course, chapter, or subsection for the recursive function

    Returns
    -------
    The complete graph of the course sections.

    """
    for neighbor in course.neighbors(level):
        ss = course.nodes[neighbor]['settings']
        if not hasattr(ss, 'activityid'):
            if ss.sub_sections:
                sub_neighbors = ss.sub_sections
                if not (archive.course.settings.format == 'flexsections' and ss.number == 0):
                    for sub_neighbor_id, sub_neighbor in enumerate(sub_neighbors):
                        ss = archive.section_list[sub_neighbor].settings
                        course.add_node(f"{neighbor}.{sub_neighbor_id + 1}",
                                        name_=ss.name,
                                        type_='chapter',
                                        settings=ss
                                        )
                        course.add_edge(neighbor,
                                        f"{neighbor}.{sub_neighbor_id + 1}"
                                        )
                        add_activities(course, archive, f"{neighbor}.{sub_neighbor_id + 1}")

                        # recursively add chapters according to the current level
                        if len(course.nodes[f"{neighbor}.{sub_neighbor_id + 1}"]['settings'].sub_sections) != 0:
                            add_chapters(course, archive, neighbor)

    return course


def add_activities(course: DiGraph, archive: MoodleArchive, node: str) -> DiGraph:
    """
    Add all activities to the Directed Graph for each node. A node can be the course, a section, or a subsection.

    Parameters
    ----------
    course: course id
    archive: the Moodle archive of the course
    node: the node to add activities to

    """
    sequence = course.nodes[node]['settings'].sequence
    for item in sequence:
        cmid = item.split('_')[1]

        for activity in archive.activities.keys():
            activity_type = activity.split('_')[0]
            activity_cmid = activity.split('_')[1]
            if cmid == activity_cmid:
                course.add_node(activity,
                                name_=archive.activities[activity].settings.name,
                                type_=activity_type,
                                settings=archive.activities[activity].settings)
                course.add_edge(node, activity)
                break

    return course


def add_interactions(course: DiGraph, archive: MoodleArchive, level):
    pass


def integrate_course_structure(df: DataFrame, course_structure: DiGraph, archive: MoodleArchive) -> DataFrame:
    # select the components to check
    excluded_components = ['Role', 'Groups', 'Grades', 'User profile', 'Enrolment', 'Attendance']

    components = list(set(df.Component.unique()) - set(excluded_components))

    # filter selected components, available activities, and students.
    df = df.loc[(df.Component.isin(components))].copy()

    for node in course_structure.nodes:
        settings = course_structure.nodes[node]['settings']
        component = node.split('_')[0].capitalize()
        if component == 'Assign':
            component = 'Assignment'
        if component == 'Lti':
            component = 'External tool'
        if component == 'Resource':
            component = 'File'
        if component == 'Url':
            component = 'URL'
        if component == 'Scorm':
            component = 'SCORM package'
        if component == 'Data':
            component = 'Database'
        if component == 'Choicegroup':
            component = 'Group choice'
        if component in components and node != 'course':
            object_id = int(node.split('_')[1])
            condition = (df.Component == component) & (df.ObjectID == object_id)
            df.loc[
                condition, 'Context'] = settings.name  # TODO: remove in the final code, but here is needed to fix hashing "context" errors.
            df.loc[condition, 'Visibility'] = settings.visible
            df.loc[condition, 'Availability'] = settings.availability
            df.loc[condition, 'Section_number'] = settings.sectionnumber

    df.loc[(df.Component == 'Course'), 'Visibility'] = True
    df.loc[(df.Component == 'Course'), 'Section_number'] = -1

    for section in archive.section_list:
        number = section.settings.number
        name = section.settings.name
        df.loc[df.Section_number == number, 'Section_name'] = name

    df.loc[df.Section_number == -1, 'Section_name'] = 'Home page'

    return df


def plot_graph(course_structure: DiGraph, figsize: tuple, textlen: int = 35):
    """
    Plot the graph of the course structure.

    Parameters
    ----------
    course_structure: directed graph of the course structure
    figsize: the size of the figure
    textlen: the length of the text in the figure

    """
    figure_plot = plt.figure(figsize=figsize)

    node_names = {}
    for node in course_structure.nodes:
        node_names[node] = course_structure.nodes[node]['name_']

    node_types = {}
    for node in course_structure.nodes:
        node_types[node] = course_structure.nodes[node]['type_']
    df = pd.DataFrame(node_types.values(), columns=['type'])
    df['type'] = pd.Categorical(df['type'])

    # label_names = {}
    # for node in course.nodes:
    #     if course.nodes[node]['type_'] != 'activity':
    #         label_names[node] = '' #course.nodes[node]['type_']
    #     else:
    #         label_names[node] = course.nodes[node]['cmtype_']

    # legend
    colors = mpl.colormaps['tab20'].colors
    color_groups = pd.DataFrame()
    color_groups['codes'] = df['type'].cat.codes
    color_groups['type'] = df['type']
    color_groups = color_groups[['codes', 'type']].reset_index(drop=True)

    color_map = []
    for i in range(len(color_groups)):
        color_map.append(colors[color_groups['codes'][i]])

    legend_elements = []
    color_groups_unique = color_groups.drop_duplicates().reset_index(drop=True)
    for i in range(len(color_groups_unique)):
        item = Line2D([0], [0],
                      marker='$\u25AC$',
                      alpha=0.7,
                      color=colors[color_groups_unique['codes'][i]],
                      label=color_groups_unique['type'][i],  # lw=0,
                      markersize=90)
        legend_elements.append(item)

    node_options = {
        'node_color': color_map,  # df['type'].cat.codes,
        'edge_color': 'tab:blue',
        'node_size': 10000,
        'alpha': 0.7,
        'node_shape': '$\u25AC$',
        'font_size': 20,
        'width': 5,
    }

    # label_options = {
    #     'font_color':'red',
    #     'font_weight':'bold',
    #     'font_size': 20,
    # }

    data = {(u, v): d for u, v, d in course_structure.edges.data()}  # create a dict of { edge : data ...}
    course_tree = nx.dfs_tree(course_structure)  # create tree
    nx.set_edge_attributes(course_tree, data)
    node_positions = graphviz_layout(course_tree, prog="dot")

    # label_positions = {}
    # for key, value in node_positions.items():
    #     label_positions[key] = (value[0], value[1]-5)

    leaf_nodes = [node for node in course_structure.nodes() if course_structure.in_degree(node) != 0
                  and course_structure.out_degree(node) == 0]
    for idx in range(len(leaf_nodes) - 1):
        if (len(course_structure.nodes[leaf_nodes[idx]]['name_']) >= textlen
                and len(course_structure.nodes[leaf_nodes[idx + 1]]['name_']) >= textlen):
            node_positions[leaf_nodes[idx]] = (
                node_positions[leaf_nodes[idx]][0], node_positions[leaf_nodes[idx]][1] - 15)
            node_positions[leaf_nodes[idx + 1]] = (
                node_positions[leaf_nodes[idx + 1]][0], node_positions[leaf_nodes[idx + 1]][1] - 30)
            if idx != 0 and node_positions[leaf_nodes[idx - 1]][1] == node_positions[leaf_nodes[idx]][1]:
                node_positions[leaf_nodes[idx]] = (
                    node_positions[leaf_nodes[idx]][0], node_positions[leaf_nodes[idx + 1]][1] - 45)

    nx.draw(course_tree, node_positions, **node_options, labels=node_names)
    # nx.draw_networkx_labels(course_tree, label_positions, **label_options, labels=label_names)

    plt.legend(handles=legend_elements, loc='upper left', fontsize=30)

    return figure_plot

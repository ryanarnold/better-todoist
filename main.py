from todoist.api import TodoistAPI

def get_label_by_name(name):
    return [l for l in api.state['labels'] if l['name'] == name][0]


def get_project_subtasks(project_id, all_items):
    return [i for i in all_items if project_id == i['parent_id'] and i['checked'] == 0 and i['is_deleted'] == 0]


def add_label(item, label):
    item_labels = item['labels']
    item_labels.append(label['id'])
    api.items.get_by_id(item['id']).update(labels=item_labels)

def remove_label(item, label):
    item_labels = item['labels']
    item_labels.remove(label['id'])
    api.items.get_by_id(item['id']).update(labels=item_labels)

if __name__ == '__main__':

    api = TodoistAPI('f0c26a6fb3e422ae93f0ad97ae895dce2c54078d')
    api.sync()

    # Load labels
    project_label = get_label_by_name('project')
    active_label = get_label_by_name('active')
    complete_label = get_label_by_name('complete')

    while True:

        api.sync()

        # Load all items
        all_items = api.state['items']

        # Load all projects
        all_projects = [p for p in all_items if project_label['id'] in p['labels']]

        for project in all_projects:

            # Retrieve first subtask of the project
            project_subtasks = get_project_subtasks(project['id'], all_items)

            if len(project_subtasks) > 0:
                first_item = project_subtasks[0]

                # Adds an @active label to the first subtask of the project if none exists yet
                if active_label['id'] not in first_item['labels']:
                    print('Adding @active to : "%s" (%s)' % (first_item['content'], first_item['id']))
                    add_label(first_item, active_label)

                # Remove @complete label if the project has subtasks
                if complete_label['id'] in project['labels']:
                    print('Remove @complete to : "%s" (%s)' % (project['content'], project['id']))
                    remove_label(project, complete_label)
            else:            
                # Adds an @complete label to the project if it doesn't have any more active task
                if complete_label['id'] not in project['labels']:
                    print('Adding @complete to : "%s" (%s)' % (project['content'], project['id']))
                    add_label(project, complete_label)

        api.commit()
        print('Passing')

from todoist.api import TodoistAPI
import time
import logging


def get_label_by_name(name):
    return [l for l in api.state['labels'] if l['name'] == name][0]


def get_project_subtasks(project_id, all_items):
    return [i for i in all_items if project_id == i['parent_id'] and i['checked'] == 0 and i['is_deleted'] == 0]


def get_topmost_subtask(project_subtasks):
    lowest_index = 1000
    
    # Identify the lowest index
    for i in project_subtasks:
        if i['child_order'] < lowest_index:
            lowest_index = i['child_order']
    
    return [i for i in project_subtasks if i['child_order'] == lowest_index][0]

def add_label(item, label):
    item_labels = item['labels']
    item_labels.append(label['id'])
    api.items.get_by_id(item['id']).update(labels=item_labels)

def remove_label(item, label):
    item_labels = item['labels']
    item_labels.remove(label['id'])
    api.items.get_by_id(item['id']).update(labels=item_labels)

if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
    logging.info('hello')

    api = TodoistAPI('f0c26a6fb3e422ae93f0ad97ae895dce2c54078d')
    api.sync()

    # Load labels
    project_label = get_label_by_name('project')
    active_label = get_label_by_name('active')
    complete_label = get_label_by_name('complete')
    waiting_label = get_label_by_name('waiting')

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
                first_item = get_topmost_subtask(project_subtasks)

                # Adds an @active label to the first subtask of the project if none exists yet
                if active_label['id'] not in first_item['labels']:
                    logging.info('Adding @active to : "%s" (%s)' % (first_item['content'], first_item['id']))
                    add_label(first_item, active_label)
                
                # Adds a @waiting label to the project if its topmost subtask has a @waiting label
                if waiting_label['id'] in first_item['labels']:
                    logging.info('Adding @waiting to: "%s"' % project['id'])
                    add_label(project, waiting_label)
                # Remove @waiting label to the project if its topmost subtask does NOT have a @waiting label
                elif waiting_label['id'] in project['labels']:
                    logging.info('Removing @waiting from: "%s"' % project['id'])
                    remove_label(project, waiting_label)

                # Remove @complete label if the project has subtasks
                if complete_label['id'] in project['labels']:
                    logging.info('Remove @complete to : "%s" (%s)' % (project['content'], project['id']))
                    remove_label(project, complete_label)
            else:            
                # Adds an @complete label to the project if it doesn't have any more active task
                if complete_label['id'] not in project['labels']:
                    logging.info('Adding @complete to : "%s" (%s)' % (project['content'], project['id']))
                    add_label(project, complete_label)
                
                # Remove @waiting label to the project if its topmost subtask does NOT have a @waiting label
                if waiting_label['id'] in project['labels']:
                    logging.info('Removing @waiting from: "%s"' % project['id'])
                    remove_label(project, waiting_label)

        if len(api.queue):
            logging.info('%d changes queued for sync... commiting to Todoist.', len(api.queue))
            api.commit()
        else:
            logging.info('No changes queued, skipping sync.')
        time.sleep(5)

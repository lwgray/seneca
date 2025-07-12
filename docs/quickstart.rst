Quick Start Guide
=================

This guide will help you get Seneca up and running in minutes.

Starting Seneca
---------------

1. **Start the Seneca server**::

    python start_seneca.py

2. **Open your browser** and navigate to http://localhost:8000

3. **View real-time conversations** as they happen in Marcus

Basic Usage
-----------

Dashboard Overview
~~~~~~~~~~~~~~~~~~

The main dashboard shows:

* **Active Conversations** - Real-time feed of agent communications
* **Task Progress** - Visual representation of task completion
* **Agent Status** - Current state of each agent
* **System Health** - Overall health score and metrics

Filtering Conversations
~~~~~~~~~~~~~~~~~~~~~~~

Use the filter panel to narrow down conversations:

* **By Agent** - Select specific agents to monitor
* **By Type** - Filter by conversation type (worker messages, decisions, blockers)
* **By Time** - Set a time range for historical analysis
* **By Task** - Focus on specific task IDs

Analyzing Patterns
~~~~~~~~~~~~~~~~~~

Click on the "Analytics" tab to see:

* Conversation frequency over time
* Agent activity patterns
* Task completion rates
* Blocker trends

Python API Usage
----------------

Basic Example
~~~~~~~~~~~~~

.. code-block:: python

    from processors.conversation_processor import ConversationProcessor
    
    # Initialize processor
    processor = ConversationProcessor("/path/to/marcus/logs")
    
    # Get recent conversations
    conversations = processor.get_recent_conversations(limit=50)
    
    # Get analytics
    analytics = processor.get_conversation_analytics(hours=24)
    print(f"Total conversations: {analytics['total_conversations']}")

Streaming Updates
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from processors.conversation_processor import ConversationStreamProcessor
    
    # Create stream processor
    stream = ConversationStreamProcessor("/path/to/marcus/logs")
    
    # Get new conversations since last check
    while True:
        new_conversations = stream.get_new_conversations()
        for conv in new_conversations:
            print(f"{conv['timestamp']}: {conv['type']} - {conv['message']}")
        time.sleep(5)  # Check every 5 seconds

RESTful API
-----------

Get Recent Conversations
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    curl http://localhost:8000/api/conversations/recent?limit=10

Get Analytics
~~~~~~~~~~~~~

.. code-block:: bash

    curl http://localhost:8000/api/analytics?hours=24

Stream Conversations
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    curl http://localhost:8000/api/stream

WebSocket Connection
--------------------

For real-time updates, connect via WebSocket:

.. code-block:: javascript

    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onmessage = (event) => {
        const conversation = JSON.parse(event.data);
        console.log('New conversation:', conversation);
    };

Common Patterns
---------------

Monitoring Task Progress
~~~~~~~~~~~~~~~~~~~~~~~~

Track a specific task through its lifecycle:

.. code-block:: python

    # Get all conversations for a task
    task_convs = [
        c for c in processor.get_recent_conversations(1000)
        if c.get('task_id') == 'TASK-123'
    ]
    
    # Analyze task timeline
    for conv in sorted(task_convs, key=lambda x: x['timestamp']):
        print(f"{conv['timestamp']}: {conv['type']}")

Identifying Bottlenecks
~~~~~~~~~~~~~~~~~~~~~~~

Find agents with the most blockers:

.. code-block:: python

    analytics = processor.get_conversation_analytics(hours=24)
    blockers = analytics['blockers']['by_agent']
    
    for agent, count in sorted(blockers.items(), key=lambda x: x[1], reverse=True):
        print(f"{agent}: {count} blockers")

Next Steps
----------

* Explore the full :doc:`api/index`
* Learn about :doc:`architecture`
* Set up :doc:`development` environment
* Read about advanced features in the API documentation
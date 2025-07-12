API Reference
=============

This section contains the complete API reference for Seneca.

Core Modules
------------

.. toctree::
   :maxdepth: 2
   
   processors
   models
   visualization

Processors Module
-----------------

The processors module contains the core functionality for reading and processing
Marcus conversation logs.

.. automodule:: processors
   :members:
   :undoc-members:
   :show-inheritance:

Key Classes
~~~~~~~~~~~

ConversationProcessor
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: processors.conversation_processor.ConversationProcessor
   :members:
   :special-members: __init__
   :show-inheritance:

ConversationStreamProcessor
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: processors.conversation_processor.ConversationStreamProcessor
   :members:
   :special-members: __init__
   :show-inheritance:

HealthMonitor
^^^^^^^^^^^^^

.. autoclass:: processors.health_monitor.HealthMonitor
   :members:
   :special-members: __init__
   :show-inheritance:

VisualizationServer
^^^^^^^^^^^^^^^^^^^

.. autoclass:: processors.ui_server.VisualizationServer
   :members:
   :special-members: __init__
   :show-inheritance:

Models Module
-------------

Data models used throughout Seneca.

.. automodule:: processors.models
   :members:
   :undoc-members:
   :show-inheritance:

Enumerations
~~~~~~~~~~~~

.. autoclass:: processors.models.TaskStatus
   :members:
   :undoc-members:

.. autoclass:: processors.models.WorkerStatus
   :members:
   :undoc-members:

.. autoclass:: processors.models.RiskLevel
   :members:
   :undoc-members:

.. autoclass:: processors.conversation_processor.ConversationType
   :members:
   :undoc-members:

Data Classes
~~~~~~~~~~~~

.. autoclass:: processors.models.Task
   :members:
   :show-inheritance:

.. autoclass:: processors.models.Worker
   :members:
   :show-inheritance:

.. autoclass:: processors.models.ProjectState
   :members:
   :show-inheritance:

REST API Endpoints
------------------

Conversations
~~~~~~~~~~~~~

.. http:get:: /api/conversations/recent

   Get recent conversations
   
   **Query Parameters:**
   
   * **limit** (*int*) -- Maximum number of conversations to return (default: 100)
   
   **Response:**
   
   .. code-block:: json
   
      [
        {
          "timestamp": "2024-01-15T10:00:00Z",
          "type": "worker_to_pm",
          "message": "Task completed",
          "agent_id": "worker_1"
        }
      ]

.. http:get:: /api/conversations/range

   Get conversations within a time range
   
   **Query Parameters:**
   
   * **start** (*string*) -- ISO format start time
   * **end** (*string*) -- ISO format end time
   * **type** (*string*) -- Optional conversation type filter
   
.. http:get:: /api/conversations/agent/(agent_id)

   Get conversations for a specific agent

Analytics
~~~~~~~~~

.. http:get:: /api/analytics

   Get conversation analytics
   
   **Query Parameters:**
   
   * **hours** (*int*) -- Number of hours to analyze (default: 24)

Health
~~~~~~

.. http:get:: /api/health

   Get system health status

.. http:get:: /api/health/analysis

   Get AI-powered health analysis

WebSocket API
-------------

.. websocket:: /ws

   Real-time conversation stream
   
   **Messages:**
   
   Each message is a JSON object representing a new conversation:
   
   .. code-block:: json
   
      {
        "type": "conversation",
        "data": {
          "timestamp": "2024-01-15T10:00:00Z",
          "type": "worker_to_pm",
          "message": "Task completed"
        }
      }
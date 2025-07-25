// Marcus Pipeline Enhancement Dashboard Application

const { createApp } = Vue;

createApp({
    delimiters: ['[[', ']]'],  // Change delimiters to avoid conflict with Jinja2
    data() {
        return {
            // Tab management
            activeTab: 'monitor',
            
            // Live Monitor
            dashboard: {
                active_flows: [],
                system_metrics: {},
                health_summary: {},
                alerts: []
            },
            socket: null,
            
            // Pipeline Replay
            replayFlowId: '',
            replaySession: null,
            replayPosition: 0,
            isPlaying: false,
            playInterval: null,
            
            // What-If Analysis
            whatifFlowId: '',
            whatifSession: null,
            modifications: [],
            simulationResults: null,
            
            // Compare Flows
            compareFlowIds: ['', ''],
            comparisonReport: null,
            
            // Recommendations
            recommendFlowId: '',
            recommendations: null,
            similarFlows: null,
            
            // Agent Management
            newAgent: {
                id: '',
                name: '',
                role: ''
            },
            registeredAgents: [],
            taskUpdate: {
                agent_id: '',
                task_id: '',
                status: 'in_progress',
                progress: 0,
                message: ''
            },
            projectStatus: null,
            agentLogs: [],
            
            // Project Management
            newProject: {
                name: '',
                description: ''
            },
            currentProject: null,
            existingProjects: [],
            sampleProjects: [],
            selectedSample: '',
            workflowOptions: {
                auto_assign: true,
                parallel_execution: true,
                continuous_monitoring: true,
                max_agents: 3
            },
            
            // AI Predictions
            predictionForm: {
                projectId: '',
                includeConfidence: true,
                taskId: '',
                agentId: '',
                blockageTaskId: '',
                includeMitigation: true,
                cascadeTaskId: '',
                delayDays: 1,
                assignmentTaskId: '',
                assignmentAgentId: ''
            },
            predictions: {
                projectCompletion: null,
                taskOutcome: null,
                blockageRisk: null,
                cascadeEffects: null,
                assignmentScore: null
            },
            
            // Analytics & Metrics
            analyticsForm: {
                timeWindow: '7d',
                agentId: '',
                agentTimeWindow: '7d',
                codeAgentId: '',
                startDate: '',
                endDate: '',
                repository: '',
                repoTimeWindow: '7d',
                qualityRepository: '',
                branch: 'main'
            },
            analytics: {
                dashboardOverview: null,
                agentMetrics: null,
                codeMetrics: null,
                repositoryMetrics: null,
                codeQuality: null
            }
        };
    },
    
    mounted() {
        console.log('Vue app mounted, activeTab:', this.activeTab);
        console.log('Dashboard data:', this.dashboard);
        this.initializeWebSocket();
        this.loadDashboard();
        this.refreshProjects();
        this.refreshAgents();
        this.loadSampleProjects();
    },
    
    methods: {
        // Tab management
        switchTab(tabName) {
            console.log('Switching to tab:', tabName);
            this.activeTab = tabName;
        },
        
        // Cost tracking methods
        async fetchProjectCosts(projectId) {
            if (!projectId) return;
            
            try {
                const response = await fetch(`/api/costs/project/${projectId}`);
                const data = await response.json();
                
                if (data.success) {
                    // Update project with real cost data
                    this.currentProject.tokenCosts = data.stats;
                    this.currentProject.costHistory = data.history;
                    this.currentProject.costComparison = data.comparison;
                    
                    // Calculate naive estimate for comparison
                    if (this.currentProject.estimated_hours) {
                        this.currentProject.naive_cost = (this.currentProject.estimated_hours * 150).toFixed(2);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch project costs:', error);
            }
        },
        
        async fetchCostSummary() {
            try {
                const response = await fetch('/api/costs/summary');
                const data = await response.json();
                
                if (data.success) {
                    this.costSummary = data.summary;
                    this.costInsights = data.insights;
                }
            } catch (error) {
                console.error('Failed to fetch cost summary:', error);
            }
        },
        
        // WebSocket Management
        initializeWebSocket() {
            this.socket = io();
            
            this.socket.on('connect', () => {
                console.log('Connected to WebSocket');
            });
            
            this.socket.on('dashboard_update', (data) => {
                this.dashboard = data;
            });
            
            this.socket.on('flow_update', (data) => {
                // Update specific flow in dashboard
                const index = this.dashboard.active_flows.findIndex(f => f.flow_id === data.flow_id);
                if (index !== -1) {
                    this.dashboard.active_flows[index] = data;
                }
            });
        },
        
        // Live Monitor Methods
        async loadDashboard() {
            try {
                const response = await fetch('/api/pipeline/monitor/dashboard');
                const data = await response.json();
                if (data.success) {
                    // Don't overwrite the entire dashboard object
                    this.dashboard.active_flows = data.active_flows || [];
                    this.dashboard.system_metrics = data.system_metrics || {};
                    this.dashboard.health_summary = data.health_summary || {};
                    this.dashboard.alerts = data.alerts || [];
                }
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        },
        
        async viewFlowDetails(flowId) {
            this.replayFlowId = flowId;
            this.activeTab = 'replay';
            await this.startReplay();
        },
        
        // Pipeline Replay Methods
        async startReplay() {
            if (!this.replayFlowId) return;
            
            try {
                const response = await fetch('/api/pipeline/replay/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ flow_id: this.replayFlowId })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.replaySession = data;
                    this.replayPosition = data.current_position;
                }
            } catch (error) {
                console.error('Failed to start replay:', error);
            }
        },
        
        async stepForward() {
            try {
                const response = await fetch('/api/pipeline/replay/forward', {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (data.success) {
                    this.replaySession.state = data.state;
                    this.replayPosition++;
                }
            } catch (error) {
                console.error('Failed to step forward:', error);
            }
        },
        
        async stepBackward() {
            try {
                const response = await fetch('/api/pipeline/replay/backward', {
                    method: 'POST'
                });
                
                const data = await response.json();
                if (data.success) {
                    this.replaySession.state = data.state;
                    this.replayPosition--;
                }
            } catch (error) {
                console.error('Failed to step backward:', error);
            }
        },
        
        async jumpToPosition() {
            try {
                const response = await fetch('/api/pipeline/replay/jump', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ position: parseInt(this.replayPosition) })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.replaySession.state = data.state;
                }
            } catch (error) {
                console.error('Failed to jump to position:', error);
            }
        },
        
        playPause() {
            if (this.isPlaying) {
                clearInterval(this.playInterval);
                this.isPlaying = false;
            } else {
                this.isPlaying = true;
                this.playInterval = setInterval(async () => {
                    if (this.replayPosition >= this.replaySession.total_events - 1) {
                        this.playPause();
                        return;
                    }
                    await this.stepForward();
                }, 1000);
            }
        },
        
        // What-If Analysis Methods
        async startWhatIf() {
            if (!this.whatifFlowId) return;
            
            try {
                const response = await fetch('/api/pipeline/whatif/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ flow_id: this.whatifFlowId })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.whatifSession = data;
                    this.modifications = [];
                }
            } catch (error) {
                console.error('Failed to start what-if analysis:', error);
            }
        },
        
        addModification() {
            this.modifications.push({
                parameter_type: 'requirement',
                parameter_name: '',
                new_value: ''
            });
        },
        
        removeModification(index) {
            this.modifications.splice(index, 1);
        },
        
        async runSimulation() {
            if (!this.modifications.length) return;
            
            try {
                const response = await fetch('/api/pipeline/whatif/simulate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ modifications: this.modifications })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.simulationResults = data.simulation;
                    this.drawWhatIfChart();
                }
            } catch (error) {
                console.error('Failed to run simulation:', error);
            }
        },
        
        drawWhatIfChart() {
            const ctx = document.getElementById('whatifChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: ['Tasks', 'Complexity', 'Cost', 'Quality'],
                    datasets: [
                        {
                            label: 'Original',
                            data: [
                                this.whatifSession.original_metrics.task_count,
                                this.whatifSession.original_metrics.complexity * 100,
                                this.whatifSession.original_metrics.cost * 10,
                                this.whatifSession.original_metrics.quality * 100
                            ],
                            borderColor: 'rgb(54, 162, 235)',
                            backgroundColor: 'rgba(54, 162, 235, 0.2)'
                        },
                        {
                            label: 'Modified',
                            data: [
                                this.simulationResults.predicted_metrics.task_count,
                                this.simulationResults.predicted_metrics.complexity * 100,
                                this.simulationResults.predicted_metrics.cost * 10,
                                this.simulationResults.predicted_metrics.quality * 100
                            ],
                            borderColor: 'rgb(255, 99, 132)',
                            backgroundColor: 'rgba(255, 99, 132, 0.2)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        r: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },
        
        // Compare Flows Methods
        addCompareFlow() {
            this.compareFlowIds.push('');
        },
        
        removeCompareFlow(index) {
            this.compareFlowIds.splice(index, 1);
        },
        
        async runComparison() {
            const validFlowIds = this.compareFlowIds.filter(id => id.trim());
            if (validFlowIds.length < 2) return;
            
            try {
                const response = await fetch('/api/pipeline/compare', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ flow_ids: validFlowIds })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.comparisonReport = data.report;
                    this.drawComparisonChart();
                }
            } catch (error) {
                console.error('Failed to compare flows:', error);
            }
        },
        
        drawComparisonChart() {
            const ctx = document.getElementById('comparisonChart').getContext('2d');
            
            const labels = this.comparisonReport.flow_summaries.map(f => f.project_name);
            
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Duration (s)',
                            data: this.comparisonReport.flow_summaries.map(f => f.duration_seconds),
                            backgroundColor: 'rgba(54, 162, 235, 0.5)'
                        },
                        {
                            label: 'Cost ($)',
                            data: this.comparisonReport.flow_summaries.map(f => f.cost),
                            backgroundColor: 'rgba(255, 99, 132, 0.5)'
                        },
                        {
                            label: 'Tasks',
                            data: this.comparisonReport.flow_summaries.map(f => f.task_count),
                            backgroundColor: 'rgba(75, 192, 192, 0.5)'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        },
        
        // Recommendations Methods
        async getRecommendations() {
            if (!this.recommendFlowId) return;
            
            try {
                const [recResponse, similarResponse] = await Promise.all([
                    fetch(`/api/pipeline/recommendations/${this.recommendFlowId}`),
                    fetch(`/api/pipeline/similar/${this.recommendFlowId}`)
                ]);
                
                const recData = await recResponse.json();
                const similarData = await similarResponse.json();
                
                if (recData.success) {
                    this.recommendations = recData.recommendations;
                }
                
                if (similarData.success) {
                    this.similarFlows = similarData.similar_flows;
                }
            } catch (error) {
                console.error('Failed to get recommendations:', error);
            }
        },
        
        async viewFlow(flowId) {
            this.replayFlowId = flowId;
            this.activeTab = 'replay';
            await this.startReplay();
        },
        
        // Agent Management Methods
        async registerAgent() {
            if (!this.newAgent.id || !this.newAgent.name || !this.newAgent.role) {
                alert('Please fill in all agent fields');
                return;
            }
            
            try {
                const response = await fetch('/api/agents/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        agent_id: this.newAgent.id,
                        name: this.newAgent.name,
                        role: this.newAgent.role,
                        skills: []
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.agentLogs.unshift({
                        timestamp: new Date().toISOString(),
                        agent_id: this.newAgent.id,
                        message: `Agent registered successfully`
                    });
                    
                    // Clear form
                    this.newAgent = { id: '', name: '', role: '' };
                    
                    // Refresh agent list
                    await this.refreshAgents();
                } else {
                    alert(`Failed to register agent: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to register agent:', error);
                alert('Failed to register agent');
            }
        },
        
        async refreshAgents() {
            try {
                const response = await fetch('/api/agents/list');
                const data = await response.json();
                
                if (data.agents) {
                    this.registeredAgents = data.agents;
                }
            } catch (error) {
                console.error('Failed to refresh agents:', error);
            }
        },
        
        async getAgentStatus(agentId) {
            try {
                const response = await fetch(`/api/agents/${agentId}/status`);
                const data = await response.json();
                
                // Update agent in list
                const index = this.registeredAgents.findIndex(a => a.agent_id === agentId);
                if (index !== -1 && data.status) {
                    this.registeredAgents[index] = {
                        ...this.registeredAgents[index],
                        ...data
                    };
                }
                
                this.agentLogs.unshift({
                    timestamp: new Date().toISOString(),
                    agent_id: agentId,
                    message: `Status: ${data.status} ${data.current_task ? '- Working on: ' + data.current_task.name : ''}`
                });
            } catch (error) {
                console.error('Failed to get agent status:', error);
            }
        },
        
        async requestTaskForAgent(agentId) {
            try {
                const response = await fetch(`/api/agents/${agentId}/request-task`, {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.task) {
                    this.agentLogs.unshift({
                        timestamp: new Date().toISOString(),
                        agent_id: agentId,
                        message: `Assigned task: ${data.task.name} (${data.task.id})`
                    });
                    
                    // Refresh agent status
                    await this.getAgentStatus(agentId);
                } else {
                    this.agentLogs.unshift({
                        timestamp: new Date().toISOString(),
                        agent_id: agentId,
                        message: data.message || 'No tasks available'
                    });
                }
            } catch (error) {
                console.error('Failed to request task:', error);
            }
        },
        
        async reportProgress() {
            if (!this.taskUpdate.agent_id || !this.taskUpdate.task_id) {
                alert('Please select agent and enter task ID');
                return;
            }
            
            try {
                const response = await fetch('/api/agents/report-progress', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.taskUpdate)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.agentLogs.unshift({
                        timestamp: new Date().toISOString(),
                        agent_id: this.taskUpdate.agent_id,
                        message: `Progress reported: ${this.taskUpdate.status} (${this.taskUpdate.progress}%)`
                    });
                    
                    // Clear form but keep agent selected
                    this.taskUpdate.task_id = '';
                    this.taskUpdate.progress = 0;
                    this.taskUpdate.message = '';
                    
                    // Refresh project status
                    await this.getProjectStatus();
                }
            } catch (error) {
                console.error('Failed to report progress:', error);
            }
        },
        
        async getProjectStatus() {
            try {
                const response = await fetch('/api/agents/project-status');
                const data = await response.json();
                
                if (data.project_state) {
                    this.projectStatus = data.project_state;
                }
            } catch (error) {
                console.error('Failed to get project status:', error);
            }
        },
        
        // Project Management Methods
        async loadSampleProjects() {
            try {
                const response = await fetch('/api/projects/samples');
                const data = await response.json();
                if (data.success) {
                    this.sampleProjects = data.samples;
                }
            } catch (error) {
                console.error('Failed to load sample projects:', error);
            }
        },
        
        loadSampleProject() {
            if (!this.selectedSample) return;
            
            const sample = this.sampleProjects.find(s => s.id === this.selectedSample);
            if (sample) {
                this.newProject.name = sample.name;
                this.newProject.description = sample.description;
            }
        },
        
        async createProject() {
            if (!this.newProject.description) {
                alert('Please provide a project description');
                return;
            }
            
            try {
                const response = await fetch('/api/projects/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.newProject)
                });
                
                const data = await response.json();
                if (data.success) {
                    this.currentProject = data.project;
                    if (data.prd_analysis) {
                        this.currentProject.prd_analysis = data.prd_analysis;
                    }
                    
                    // Fetch real-time token-based costs
                    await this.fetchProjectCosts(this.currentProject.id);
                    
                    // Clear form
                    this.newProject = { name: '', description: '' };
                    this.selectedSample = '';
                    
                    // Refresh projects list
                    await this.refreshProjects();
                } else {
                    alert(`Failed to create project: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to create project:', error);
                alert('Failed to create project');
            }
        },
        
        async addFeature() {
            if (!this.newFeature.title || !this.newFeature.description) {
                alert('Please fill in feature title and description');
                return;
            }
            
            try {
                const feature = {
                    ...this.newFeature,
                    acceptance_criteria: this.newFeature.acceptance_criteria
                        .split(',')
                        .map(c => c.trim())
                        .filter(c => c.length > 0),
                    project_id: this.currentProject.id
                };
                
                const response = await fetch('/api/projects/features/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(feature)
                });
                
                const data = await response.json();
                if (data.success) {
                    this.projectFeatures.push(data.feature);
                    
                    // Clear form
                    this.newFeature = {
                        title: '',
                        description: '',
                        priority: 'medium',
                        acceptance_criteria: ''
                    };
                } else {
                    alert(`Failed to add feature: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to add feature:', error);
                alert('Failed to add feature');
            }
        },
        
        async removeFeature(featureId) {
            try {
                const response = await fetch(`/api/projects/features/${featureId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                if (data.success) {
                    this.projectFeatures = this.projectFeatures.filter(f => f.id !== featureId);
                }
            } catch (error) {
                console.error('Failed to remove feature:', error);
            }
        },
        
        async startWorkflow() {
            if (!this.currentProject) {
                alert('Please create a project first');
                return;
            }
            
            try {
                const response = await fetch('/api/projects/workflow/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        project_id: this.currentProject.id,
                        options: this.workflowOptions
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.currentProject.status = 'running';
                    this.currentProject.flow_id = data.flow_id;
                    
                    // Switch to monitor tab to see the flow
                    this.activeTab = 'monitor';
                    
                    alert(`Workflow started! Flow ID: ${data.flow_id}`);
                } else {
                    alert(`Failed to start workflow: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to start workflow:', error);
                alert('Failed to start workflow');
            }
        },
        
        async pauseWorkflow() {
            try {
                const response = await fetch('/api/projects/workflow/pause', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        project_id: this.currentProject.id
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.currentProject.status = 'paused';
                }
            } catch (error) {
                console.error('Failed to pause workflow:', error);
            }
        },
        
        async stopWorkflow() {
            if (!confirm('Are you sure you want to stop the workflow?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/projects/workflow/stop', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        project_id: this.currentProject.id
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.currentProject.status = 'stopped';
                }
            } catch (error) {
                console.error('Failed to stop workflow:', error);
            }
        },
        
        async refreshProjects() {
            try {
                const response = await fetch('/api/projects/list');
                const data = await response.json();
                
                if (data.projects) {
                    this.existingProjects = data.projects;
                }
            } catch (error) {
                console.error('Failed to refresh projects:', error);
            }
        },
        
        async selectProject(projectId) {
            try {
                const response = await fetch(`/api/projects/${projectId}`);
                const data = await response.json();
                
                if (data.project) {
                    this.currentProject = data.project;
                    
                    // Calculate estimated cost if we have hours
                    // Fetch real-time costs after creation
                    await this.fetchProjectCosts(this.currentProject.id);
                }
            } catch (error) {
                console.error('Failed to select project:', error);
            }
        },
        
        async viewProjectFlow(projectId) {
            try {
                const response = await fetch(`/api/projects/${projectId}/flow`);
                const data = await response.json();
                
                if (data.flow_id) {
                    this.replayFlowId = data.flow_id;
                    this.activeTab = 'replay';
                    await this.startReplay();
                } else {
                    alert('No flow associated with this project yet');
                }
            } catch (error) {
                console.error('Failed to get project flow:', error);
            }
        },
        
        // AI Predictions Methods
        async predictProjectCompletion() {
            if (!this.predictionForm.projectId.trim()) {
                alert('Please enter a Project ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/predictions/project/${this.predictionForm.projectId}/completion`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        include_confidence: this.predictionForm.includeConfidence
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.predictions.projectCompletion = data;
                } else {
                    alert(`Prediction failed: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to predict project completion:', error);
                alert('Failed to get prediction. Check console for details.');
            }
        },
        
        async predictTaskOutcome() {
            if (!this.predictionForm.taskId.trim()) {
                alert('Please enter a Task ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/predictions/task/${this.predictionForm.taskId}/outcome`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        agent_id: this.predictionForm.agentId.trim() || null
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.predictions.taskOutcome = data;
                } else {
                    alert(`Prediction failed: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to predict task outcome:', error);
                alert('Failed to get prediction. Check console for details.');
            }
        },
        
        async predictBlockageRisk() {
            if (!this.predictionForm.blockageTaskId.trim()) {
                alert('Please enter a Task ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/predictions/task/${this.predictionForm.blockageTaskId}/blockage-risk`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        include_mitigation: this.predictionForm.includeMitigation
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.predictions.blockageRisk = data;
                } else {
                    alert(`Prediction failed: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to predict blockage risk:', error);
                alert('Failed to get prediction. Check console for details.');
            }
        },
        
        async predictCascadeEffects() {
            if (!this.predictionForm.cascadeTaskId.trim()) {
                alert('Please enter a Task ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/predictions/task/${this.predictionForm.cascadeTaskId}/cascade-effects`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        delay_days: this.predictionForm.delayDays
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.predictions.cascadeEffects = data;
                } else {
                    alert(`Prediction failed: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to predict cascade effects:', error);
                alert('Failed to get prediction. Check console for details.');
            }
        },
        
        async getAssignmentScore() {
            if (!this.predictionForm.assignmentTaskId.trim() || !this.predictionForm.assignmentAgentId.trim()) {
                alert('Please enter both Task ID and Agent ID');
                return;
            }
            
            try {
                const response = await fetch('/api/predictions/assignment/score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        task_id: this.predictionForm.assignmentTaskId,
                        agent_id: this.predictionForm.assignmentAgentId
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    this.predictions.assignmentScore = data;
                } else {
                    alert(`Scoring failed: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to get assignment score:', error);
                alert('Failed to get score. Check console for details.');
            }
        },
        
        // Helper methods for styling
        getBlockageRiskClass(risk) {
            if (!risk) return '';
            if (risk < 0.3) return 'risk-low';
            if (risk < 0.7) return 'risk-medium';
            return 'risk-high';
        },
        
        getScoreClass(score) {
            if (!score) return 'score-poor';
            if (score >= 0.9) return 'score-excellent';
            if (score >= 0.75) return 'score-good';
            if (score >= 0.5) return 'score-fair';
            return 'score-poor';
        },
        
        // Analytics & Metrics Methods
        async loadDashboardOverview() {
            try {
                const response = await fetch(`/api/analytics/dashboard/overview?time_window=${this.analyticsForm.timeWindow}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                if (data.success) {
                    this.analytics.dashboardOverview = data;
                    
                    // Render task breakdown chart if data available
                    this.$nextTick(() => {
                        if (data.data.task_breakdown) {
                            this.renderTaskBreakdownChart(data.data.task_breakdown);
                        }
                    });
                } else {
                    alert(`Failed to load overview: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to load dashboard overview:', error);
                alert('Failed to load overview. Check console for details.');
            }
        },
        
        async loadAgentMetrics() {
            if (!this.analyticsForm.agentId.trim()) {
                alert('Please enter an Agent ID');
                return;
            }
            
            try {
                const response = await fetch(`/api/analytics/agent/${this.analyticsForm.agentId}/metrics?time_window=${this.analyticsForm.agentTimeWindow}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                if (data.success) {
                    this.analytics.agentMetrics = data;
                } else {
                    alert(`Failed to load agent metrics: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to load agent metrics:', error);
                alert('Failed to load agent metrics. Check console for details.');
            }
        },
        
        async loadCodeMetrics() {
            if (!this.analyticsForm.codeAgentId.trim()) {
                alert('Please enter an Agent ID');
                return;
            }
            
            try {
                let url = `/api/analytics/code/${this.analyticsForm.codeAgentId}/metrics`;
                let params = new URLSearchParams();
                
                if (this.analyticsForm.startDate) {
                    params.append('start_date', this.analyticsForm.startDate);
                }
                if (this.analyticsForm.endDate) {
                    params.append('end_date', this.analyticsForm.endDate);
                }
                
                if (params.toString()) {
                    url += '?' + params.toString();
                }
                
                const response = await fetch(url, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                if (data.success) {
                    this.analytics.codeMetrics = data;
                } else {
                    alert(`Failed to load code metrics: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to load code metrics:', error);
                alert('Failed to load code metrics. Check console for details.');
            }
        },
        
        async loadRepositoryMetrics() {
            if (!this.analyticsForm.repository.trim()) {
                alert('Please enter a repository name');
                return;
            }
            
            try {
                const response = await fetch(`/api/analytics/repository/${this.analyticsForm.repository}/metrics?time_window=${this.analyticsForm.repoTimeWindow}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                if (data.success) {
                    this.analytics.repositoryMetrics = data;
                    
                    // Render repository language chart
                    this.$nextTick(() => {
                        if (data.data.language_breakdown) {
                            this.renderRepoLanguageChart(data.data.language_breakdown);
                        }
                    });
                } else {
                    alert(`Failed to load repository metrics: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to load repository metrics:', error);
                alert('Failed to load repository metrics. Check console for details.');
            }
        },
        
        async loadCodeQualityMetrics() {
            if (!this.analyticsForm.qualityRepository.trim()) {
                alert('Please enter a repository name');
                return;
            }
            
            try {
                const branch = this.analyticsForm.branch.trim() || 'main';
                const response = await fetch(`/api/analytics/code-quality/${this.analyticsForm.qualityRepository}/metrics?branch=${branch}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                if (data.success) {
                    this.analytics.codeQuality = data;
                } else {
                    alert(`Failed to load code quality metrics: ${data.error}`);
                }
            } catch (error) {
                console.error('Failed to load code quality metrics:', error);
                alert('Failed to load code quality metrics. Check console for details.');
            }
        },
        
        // Chart rendering methods
        renderTaskBreakdownChart(taskData) {
            const canvas = document.getElementById('taskBreakdownChart');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            
            // Simple pie chart implementation
            const total = Object.values(taskData).reduce((sum, count) => sum + count, 0);
            const colors = ['#007bff', '#28a745', '#ffc107', '#dc3545', '#6c757d'];
            
            let startAngle = 0;
            Object.entries(taskData).forEach(([status, count], index) => {
                const sliceAngle = (count / total) * 2 * Math.PI;
                
                ctx.beginPath();
                ctx.arc(150, 100, 80, startAngle, startAngle + sliceAngle);
                ctx.lineTo(150, 100);
                ctx.fillStyle = colors[index % colors.length];
                ctx.fill();
                
                startAngle += sliceAngle;
            });
        },
        
        renderRepoLanguageChart(languageData) {
            const canvas = document.getElementById('repoLanguageChart');
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const colors = this.getLanguageColors(Object.keys(languageData));
            
            // Simple bar chart
            const maxValue = Math.max(...Object.values(languageData));
            const barWidth = 300 / Object.keys(languageData).length - 10;
            
            Object.entries(languageData).forEach(([language, percentage], index) => {
                const barHeight = (percentage / maxValue) * 150;
                const x = index * (barWidth + 10) + 20;
                const y = 180 - barHeight;
                
                ctx.fillStyle = colors[index];
                ctx.fillRect(x, y, barWidth, barHeight);
                
                // Label
                ctx.fillStyle = '#000';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(language, x + barWidth/2, 195);
            });
        },
        
        // Helper methods for styling
        getHealthScoreClass(score) {
            if (!score) return '';
            if (score >= 0.9) return 'health-excellent';
            if (score >= 0.75) return 'health-good';
            if (score >= 0.5) return 'health-fair';
            return 'health-poor';
        },
        
        getUtilizationClass(utilization) {
            if (!utilization) return 'utilization-low';
            if (utilization >= 80) return 'utilization-high';
            if (utilization >= 50) return 'utilization-medium';
            return 'utilization-low';
        },
        
        getLanguageColor(language) {
            const colors = {
                'javascript': '#f7df1e',
                'python': '#3776ab',
                'java': '#ed8b00',
                'typescript': '#3178c6',
                'go': '#00add8',
                'rust': '#ce422b',
                'cpp': '#00599c',
                'csharp': '#239120',
                'php': '#777bb4',
                'ruby': '#cc342d'
            };
            return colors[language.toLowerCase()] || '#6c757d';
        },
        
        getLanguageColors(languages) {
            return languages.map(lang => this.getLanguageColor(lang));
        },
        
        getCoverageClass(coverage) {
            if (!coverage) return 'coverage-poor';
            if (coverage >= 0.8) return 'coverage-excellent';
            if (coverage >= 0.6) return 'coverage-good';
            if (coverage >= 0.4) return 'coverage-fair';
            return 'coverage-poor';
        },
        
        getComplexityClass(complexity) {
            if (!complexity) return 'complexity-low';
            if (complexity >= 10) return 'complexity-high';
            if (complexity >= 5) return 'complexity-medium';
            return 'complexity-low';
        },
        
        getDebtClass(hours) {
            if (!hours) return 'debt-low';
            if (hours >= 40) return 'debt-high';
            if (hours >= 20) return 'debt-medium';
            return 'debt-low';
        },
        
        getSecurityClass(issues) {
            if (!issues || issues === 0) return 'security-none';
            if (issues >= 5) return 'security-high';
            return 'security-low';
        }
    }
}).mount('#app');
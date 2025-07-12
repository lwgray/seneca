// Marcus Conversation Visualization Application
const { createApp } = Vue;

createApp({
    data() {
        return {
            // Connection state
            isConnected: false,
            socket: null,
            currentTime: new Date().toLocaleTimeString(),
            
            // Conversations data
            conversations: [],
            filteredConversations: [],
            loading: true,
            hasMore: true,
            offset: 0,
            limit: 50,
            
            // Filters
            filters: {
                agentId: '',
                types: {
                    worker_message: true,
                    pm_decision: true,
                    pm_thinking: true,
                    blocker: true
                },
                timeRange: 60 // minutes
            },
            
            // Search
            searchQuery: '',
            searchDebounceTimer: null,
            
            // Active agents
            activeAgents: [],
            
            // Statistics
            stats: {
                messagesPerHour: 0,
                activeAgents: 0,
                avgConfidence: 0
            },
            
            // Analytics
            showAnalytics: false,
            analytics: {
                totalTasks: 0,
                completionRate: 0,
                avgResponseTime: 0,
                blockerCount: 0
            },
            
            // Marcus thinking indicator
            marcusThinking: false,
            marcusThought: '',
            
            // Charts
            charts: {
                volume: null,
                activity: null,
                confidence: null
            }
        };
    },
    
    mounted() {
        this.initializeWebSocket();
        this.loadRecentConversations();
        this.startTimeUpdater();
    },
    
    beforeUnmount() {
        if (this.socket) {
            this.socket.disconnect();
        }
        
        // Clean up charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    },
    
    computed: {
        debouncedSearch() {
            return () => {
                clearTimeout(this.searchDebounceTimer);
                this.searchDebounceTimer = setTimeout(() => {
                    this.performSearch();
                }, 300);
            };
        }
    },
    
    methods: {
        // WebSocket connection
        initializeWebSocket() {
            this.socket = io('/conversations', {
                transports: ['websocket']
            });
            
            this.socket.on('connect', () => {
                console.log('Connected to conversation stream');
                this.isConnected = true;
                
                // Subscribe to conversation stream
                this.socket.emit('subscribe', {
                    filters: this.filters
                });
            });
            
            this.socket.on('disconnect', () => {
                console.log('Disconnected from conversation stream');
                this.isConnected = false;
            });
            
            // Real-time conversation updates
            this.socket.on('conversation', (data) => {
                this.handleNewConversation(data);
            });
            
            // Marcus thinking updates
            this.socket.on('marcus_thinking', (data) => {
                this.marcusThinking = true;
                this.marcusThought = data.thought;
                
                // Auto-hide after a few seconds
                setTimeout(() => {
                    this.marcusThinking = false;
                }, 5000);
            });
            
            // Active agents update
            this.socket.on('agents_update', (data) => {
                this.activeAgents = data.agents;
                this.updateStats();
            });
        },
        
        // Load initial conversations
        async loadRecentConversations() {
            this.loading = true;
            
            try {
                const params = new URLSearchParams({
                    limit: this.limit,
                    offset: this.offset,
                    time_range: this.filters.timeRange
                });
                
                if (this.filters.agentId) {
                    params.append('agent_id', this.filters.agentId);
                }
                
                const response = await fetch(`/api/conversations/recent?${params}`);
                const data = await response.json();
                
                if (data.success) {
                    this.conversations = data.conversations;
                    this.filteredConversations = this.applyClientFilters(data.conversations);
                    this.hasMore = data.total > (this.offset + this.limit);
                    
                    // Update stats
                    if (data.statistics) {
                        this.updateStatsFromServer(data.statistics);
                    }
                    
                    // Load analytics if showing
                    if (this.showAnalytics) {
                        await this.loadAnalytics();
                    }
                }
            } catch (error) {
                console.error('Failed to load conversations:', error);
            } finally {
                this.loading = false;
            }
        },
        
        // Handle new conversation from WebSocket
        handleNewConversation(conversation) {
            // Add to beginning of array
            this.conversations.unshift(conversation);
            
            // Limit array size
            if (this.conversations.length > 1000) {
                this.conversations.pop();
            }
            
            // Re-apply filters
            this.filteredConversations = this.applyClientFilters(this.conversations);
            
            // Update stats in real-time
            this.updateStats();
            
            // Flash effect for new message
            this.$nextTick(() => {
                const element = document.querySelector(`[data-conversation-id="${conversation.id}"]`);
                if (element) {
                    element.classList.add('flash-new');
                    setTimeout(() => {
                        element.classList.remove('flash-new');
                    }, 1000);
                }
            });
        },
        
        // Apply client-side filters
        applyClientFilters(conversations) {
            return conversations.filter(conv => {
                // Type filter
                const typeKey = conv.type || 'worker_message';
                if (!this.filters.types[typeKey]) {
                    return false;
                }
                
                // Search filter
                if (this.searchQuery) {
                    const searchLower = this.searchQuery.toLowerCase();
                    const message = (conv.message || '').toLowerCase();
                    const metadata = JSON.stringify(conv.metadata || {}).toLowerCase();
                    
                    if (!message.includes(searchLower) && !metadata.includes(searchLower)) {
                        return false;
                    }
                }
                
                return true;
            });
        },
        
        // Load more conversations
        async loadMore() {
            this.offset += this.limit;
            this.loading = true;
            
            try {
                const params = new URLSearchParams({
                    limit: this.limit,
                    offset: this.offset,
                    time_range: this.filters.timeRange
                });
                
                const response = await fetch(`/api/conversations/recent?${params}`);
                const data = await response.json();
                
                if (data.success) {
                    this.conversations.push(...data.conversations);
                    this.filteredConversations = this.applyClientFilters(this.conversations);
                    this.hasMore = data.total > (this.offset + this.limit);
                }
            } catch (error) {
                console.error('Failed to load more conversations:', error);
            } finally {
                this.loading = false;
            }
        },
        
        // Search conversations
        async performSearch() {
            if (!this.searchQuery) {
                this.filteredConversations = this.applyClientFilters(this.conversations);
                return;
            }
            
            try {
                const response = await fetch('/api/conversations/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: this.searchQuery,
                        type: 'text',
                        filters: this.filters
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.filteredConversations = data.results;
                }
            } catch (error) {
                console.error('Search failed:', error);
                // Fall back to client-side filtering
                this.filteredConversations = this.applyClientFilters(this.conversations);
            }
        },
        
        // Load analytics data
        async loadAnalytics() {
            try {
                const response = await fetch(`/api/conversations/analytics?hours=24`);
                const data = await response.json();
                
                if (data.success) {
                    this.updateAnalytics(data.analytics);
                    this.renderCharts(data.analytics);
                }
            } catch (error) {
                console.error('Failed to load analytics:', error);
            }
        },
        
        // Update analytics
        updateAnalytics(analytics) {
            // Calculate key metrics
            const taskFlow = analytics.task_flow || {};
            this.analytics.totalTasks = taskFlow.total_tasks || 0;
            this.analytics.completionRate = Math.round((taskFlow.completion_rate || 0) * 100);
            this.analytics.avgResponseTime = analytics.response_times?.average_ms || 0;
            this.analytics.blockerCount = analytics.blocker_frequency?.total || 0;
        },
        
        // Render analytics charts
        renderCharts(analytics) {
            // Message Volume Chart
            if (analytics.message_volume) {
                this.renderVolumeChart(analytics.message_volume);
            }
            
            // Agent Activity Chart
            if (analytics.agent_activity) {
                this.renderActivityChart(analytics.agent_activity);
            }
            
            // Confidence Chart
            if (analytics.decision_confidence) {
                this.renderConfidenceChart(analytics.decision_confidence);
            }
        },
        
        renderVolumeChart(volumeData) {
            const ctx = document.getElementById('volumeChart');
            if (!ctx) return;
            
            if (this.charts.volume) {
                this.charts.volume.destroy();
            }
            
            const labels = volumeData.series.map(d => new Date(d.time).toLocaleTimeString());
            const data = volumeData.series.map(d => d.value);
            
            this.charts.volume = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Messages',
                        data: data,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        },
        
        renderActivityChart(activityData) {
            const ctx = document.getElementById('activityChart');
            if (!ctx) return;
            
            if (this.charts.activity) {
                this.charts.activity.destroy();
            }
            
            const agents = Object.keys(activityData);
            const messagesSent = agents.map(a => activityData[a].messages_sent);
            
            this.charts.activity = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: agents,
                    datasets: [{
                        label: 'Messages Sent',
                        data: messagesSent,
                        backgroundColor: '#10b981'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        },
        
        renderConfidenceChart(confidenceData) {
            const ctx = document.getElementById('confidenceChart');
            if (!ctx) return;
            
            if (this.charts.confidence) {
                this.charts.confidence.destroy();
            }
            
            const distribution = confidenceData.distribution || {};
            
            this.charts.confidence = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['High', 'Medium', 'Low'],
                    datasets: [{
                        data: [
                            distribution.high || 0,
                            distribution.medium || 0,
                            distribution.low || 0
                        ],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        },
        
        // Update statistics
        updateStats() {
            // Messages per hour
            const now = new Date();
            const hourAgo = new Date(now - 60 * 60 * 1000);
            const recentMessages = this.conversations.filter(c => 
                new Date(c.timestamp) > hourAgo
            );
            this.stats.messagesPerHour = recentMessages.length;
            
            // Active agents
            const uniqueAgents = new Set();
            this.conversations.forEach(c => {
                if (c.source && c.source.includes('agent')) {
                    uniqueAgents.add(c.source);
                }
                if (c.target && c.target.includes('agent')) {
                    uniqueAgents.add(c.target);
                }
            });
            this.stats.activeAgents = uniqueAgents.size;
            
            // Average confidence
            const decisions = this.conversations.filter(c => 
                c.type === 'pm_decision' && c.metadata?.confidence_score
            );
            if (decisions.length > 0) {
                const totalConfidence = decisions.reduce((sum, d) => 
                    sum + (d.metadata.confidence_score || 0), 0
                );
                this.stats.avgConfidence = totalConfidence / decisions.length;
            }
        },
        
        updateStatsFromServer(serverStats) {
            if (serverStats.average_decision_confidence !== undefined) {
                this.stats.avgConfidence = serverStats.average_decision_confidence;
            }
            if (serverStats.unique_agents !== undefined) {
                this.stats.activeAgents = serverStats.unique_agents;
            }
        },
        
        // UI Helper methods
        getMessageClass(conv) {
            if (conv.source && conv.source.includes('agent')) {
                return 'agent';
            }
            if (conv.source === 'marcus') {
                return 'marcus';
            }
            return 'system';
        },
        
        getSourceIcon(conv) {
            if (conv.source && conv.source.includes('agent')) {
                return 'fas fa-user-circle text-blue-400';
            }
            if (conv.source === 'marcus') {
                return 'fas fa-brain text-purple-400';
            }
            if (conv.source === 'kanban_board') {
                return 'fas fa-tasks text-green-400';
            }
            return 'fas fa-cog text-gray-400';
        },
        
        getStatusClass(status) {
            const statusMap = {
                'completed': 'px-2 py-1 bg-green-900 bg-opacity-30 text-green-400 text-xs rounded',
                'in_progress': 'px-2 py-1 bg-blue-900 bg-opacity-30 text-blue-400 text-xs rounded',
                'blocked': 'px-2 py-1 bg-red-900 bg-opacity-30 text-red-400 text-xs rounded',
                'pending': 'px-2 py-1 bg-gray-800 text-gray-400 text-xs rounded'
            };
            return statusMap[status] || statusMap['pending'];
        },
        
        getConfidenceClass(confidence) {
            if (confidence >= 0.8) return 'confidence-high';
            if (confidence >= 0.5) return 'confidence-medium';
            return 'confidence-low';
        },
        
        getCustomMetadata(metadata) {
            // Filter out common keys to show only custom ones
            const commonKeys = ['task_id', 'confidence_score', 'status', 'alternatives'];
            const custom = {};
            
            Object.keys(metadata).forEach(key => {
                if (!commonKeys.includes(key) && metadata[key]) {
                    custom[key] = metadata[key];
                }
            });
            
            return custom;
        },
        
        formatTime(timestamp) {
            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) { // Less than 1 minute
                return 'just now';
            } else if (diff < 3600000) { // Less than 1 hour
                const minutes = Math.floor(diff / 60000);
                return `${minutes}m ago`;
            } else if (diff < 86400000) { // Less than 1 day
                const hours = Math.floor(diff / 3600000);
                return `${hours}h ago`;
            } else {
                return date.toLocaleString();
            }
        },
        
        // Export conversations
        async exportConversations() {
            const dataStr = JSON.stringify(this.filteredConversations, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileDefaultName = `marcus_conversations_${new Date().toISOString()}.json`;
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileDefaultName);
            linkElement.click();
        },
        
        // Time updater
        startTimeUpdater() {
            setInterval(() => {
                this.currentTime = new Date().toLocaleTimeString();
            }, 1000);
        }
    }
}).mount('#app');

// Add CSS for flash effect
const style = document.createElement('style');
style.textContent = `
    .flash-new {
        animation: flashNew 1s ease-out;
    }
    
    @keyframes flashNew {
        0% {
            background-color: rgba(59, 130, 246, 0.3);
            transform: translateX(-5px);
        }
        100% {
            background-color: transparent;
            transform: translateX(0);
        }
    }
    
    /* Transition animations */
    .message-enter-active, .message-leave-active {
        transition: all 0.3s ease;
    }
    
    .message-enter-from {
        opacity: 0;
        transform: translateY(-10px);
    }
    
    .message-leave-to {
        opacity: 0;
        transform: translateX(20px);
    }
    
    .fade-enter-active, .fade-leave-active {
        transition: opacity 0.3s ease;
    }
    
    .fade-enter-from, .fade-leave-to {
        opacity: 0;
    }
`;
document.head.appendChild(style);
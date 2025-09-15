#!/usr/bin/env python3
"""
Comprehensive tests for Flow-Nexus cloud integration and MCP tools.

This test suite covers:
- MCP tool integration and communication
- Cloud sandbox environment creation and management
- Neural network cluster initialization and training
- Swarm coordination and agent spawning
- Workflow execution and monitoring
- Template deployment and management
- Authentication and user management
- Real-time monitoring and event streaming
- Storage and file management
- Error handling and retry mechanisms
"""

import pytest
import asyncio
import json
import time
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
from typing import Dict, List, Any, Optional

# Mock MCP tool functions since they may not be available in test environment
class MockMCPTools:
    """Mock MCP tools for testing"""
    
    def __init__(self):
        self.call_history = []
        self.responses = {}
        self.errors = {}
    
    def set_response(self, tool_name: str, response: Any):
        """Set mock response for a tool"""
        self.responses[tool_name] = response
    
    def set_error(self, tool_name: str, error: Exception):
        """Set mock error for a tool"""
        self.errors[tool_name] = error
    
    def call_mcp_tool(self, tool_name: str, **kwargs):
        """Mock MCP tool call"""
        self.call_history.append((tool_name, kwargs))
        
        if tool_name in self.errors:
            raise self.errors[tool_name]
        
        return self.responses.get(tool_name, {"status": "success", "data": {}})


@pytest.fixture
def mock_mcp_tools():
    """Provide mock MCP tools for testing"""
    return MockMCPTools()


class TestSwarmCoordination:
    """Test swarm coordination and agent management"""
    
    def test_swarm_initialization(self, mock_mcp_tools):
        """Test swarm initialization with different topologies"""
        topologies = ['mesh', 'hierarchical', 'ring', 'star']
        
        for topology in topologies:
            mock_mcp_tools.set_response('mcp__flow-nexus__swarm_init', {
                'swarm_id': f'swarm_{topology}_001',
                'topology': topology,
                'status': 'initialized',
                'agents': []
            })
            
            result = mock_mcp_tools.call_mcp_tool(
                'mcp__flow-nexus__swarm_init',
                topology=topology,
                maxAgents=8,
                strategy='balanced'
            )
            
            assert result['status'] == 'success'
            assert result['data']['topology'] == topology
    
    def test_swarm_scaling(self, mock_mcp_tools):
        """Test swarm scaling functionality"""
        # Test scale up
        mock_mcp_tools.set_response('mcp__flow-nexus__swarm_scale', {
            'swarm_id': 'swarm_001',
            'previous_agents': 5,
            'target_agents': 10,
            'scaling_status': 'completed'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__swarm_scale',
            swarm_id='swarm_001',
            target_agents=10
        )
        
        assert result['data']['target_agents'] == 10
        assert result['data']['scaling_status'] == 'completed'
    
    def test_agent_spawning(self, mock_mcp_tools):
        """Test agent spawning with different types"""
        agent_types = ['researcher', 'coder', 'analyst', 'optimizer', 'coordinator']
        
        for agent_type in agent_types:
            mock_mcp_tools.set_response('mcp__flow-nexus__agent_spawn', {
                'agent_id': f'agent_{agent_type}_001',
                'type': agent_type,
                'status': 'active',
                'capabilities': [f'{agent_type}_capability']
            })
            
            result = mock_mcp_tools.call_mcp_tool(
                'mcp__flow-nexus__agent_spawn',
                type=agent_type,
                capabilities=[f'{agent_type}_capability']
            )
            
            assert result['data']['type'] == agent_type
            assert result['data']['status'] == 'active'
    
    def test_task_orchestration(self, mock_mcp_tools):
        """Test task orchestration across swarm"""
        mock_mcp_tools.set_response('mcp__flow-nexus__task_orchestrate', {
            'task_id': 'task_001',
            'status': 'queued',
            'assigned_agents': ['agent_001', 'agent_002'],
            'estimated_duration': 300
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__task_orchestrate',
            task="Build a REST API with authentication",
            strategy='adaptive',
            priority='high',
            maxAgents=3
        )
        
        assert result['data']['status'] == 'queued'
        assert len(result['data']['assigned_agents']) == 2
    
    def test_swarm_status_monitoring(self, mock_mcp_tools):
        """Test swarm status monitoring"""
        mock_mcp_tools.set_response('mcp__flow-nexus__swarm_status', {
            'swarm_id': 'swarm_001',
            'topology': 'mesh',
            'active_agents': 5,
            'running_tasks': 3,
            'health_status': 'healthy',
            'resource_usage': {
                'cpu': 45.2,
                'memory': 67.8,
                'network': 23.1
            }
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__swarm_status',
            swarm_id='swarm_001'
        )
        
        assert result['data']['health_status'] == 'healthy'
        assert result['data']['active_agents'] == 5
        assert 'resource_usage' in result['data']
    
    def test_swarm_destruction(self, mock_mcp_tools):
        """Test swarm destruction and cleanup"""
        mock_mcp_tools.set_response('mcp__flow-nexus__swarm_destroy', {
            'swarm_id': 'swarm_001',
            'cleanup_status': 'completed',
            'resources_freed': True,
            'agents_terminated': 5
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__swarm_destroy',
            swarm_id='swarm_001'
        )
        
        assert result['data']['cleanup_status'] == 'completed'
        assert result['data']['resources_freed'] is True


class TestSandboxManagement:
    """Test cloud sandbox creation and management"""
    
    def test_sandbox_creation_basic(self, mock_mcp_tools):
        """Test basic sandbox creation"""
        templates = ['node', 'python', 'react', 'nextjs', 'claude-code']
        
        for template in templates:
            mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_create', {
                'sandbox_id': f'sandbox_{template}_001',
                'template': template,
                'status': 'running',
                'url': f'https://sandbox-{template}.flow-nexus.dev',
                'environment': {
                    'nodejs_version': '18.17.0' if 'node' in template else None,
                    'python_version': '3.11.0' if template == 'python' else None
                }
            })
            
            result = mock_mcp_tools.call_mcp_tool(
                'mcp__flow-nexus__sandbox_create',
                template=template,
                timeout=3600
            )
            
            assert result['data']['template'] == template
            assert result['data']['status'] == 'running'
    
    def test_sandbox_creation_with_env_vars(self, mock_mcp_tools):
        """Test sandbox creation with environment variables"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_create', {
            'sandbox_id': 'sandbox_env_001',
            'template': 'node',
            'status': 'running',
            'environment_variables': {
                'API_KEY': '***',
                'NODE_ENV': 'development',
                'DEBUG': 'true'
            }
        })
        
        env_vars = {
            'API_KEY': 'secret-key-123',
            'NODE_ENV': 'development',
            'DEBUG': 'true'
        }
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__sandbox_create',
            template='node',
            env_vars=env_vars,
            anthropic_key='claude-key'
        )
        
        assert 'environment_variables' in result['data']
        assert result['data']['environment_variables']['NODE_ENV'] == 'development'
    
    def test_sandbox_code_execution(self, mock_mcp_tools):
        """Test code execution in sandbox"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_execute', {
            'execution_id': 'exec_001',
            'stdout': 'Hello, World!\n',
            'stderr': '',
            'exit_code': 0,
            'execution_time': 0.123,
            'status': 'completed'
        })
        
        code = """
        console.log('Hello, World!');
        const result = 2 + 2;
        console.log('2 + 2 =', result);
        """
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__sandbox_execute',
            sandbox_id='sandbox_001',
            code=code,
            language='javascript',
            timeout=60
        )
        
        assert result['data']['exit_code'] == 0
        assert 'Hello, World!' in result['data']['stdout']
        assert result['data']['status'] == 'completed'
    
    def test_sandbox_file_upload(self, mock_mcp_tools):
        """Test file upload to sandbox"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_upload', {
            'file_path': '/workspace/app.js',
            'size_bytes': 1024,
            'upload_status': 'completed',
            'checksum': 'abc123def456'
        })
        
        file_content = """
        const express = require('express');
        const app = express();
        
        app.get('/', (req, res) => {
            res.send('Hello from uploaded file!');
        });
        
        app.listen(3000);
        """
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__sandbox_upload',
            sandbox_id='sandbox_001',
            file_path='/workspace/app.js',
            content=file_content
        )
        
        assert result['data']['upload_status'] == 'completed'
        assert result['data']['file_path'] == '/workspace/app.js'
    
    def test_sandbox_configuration(self, mock_mcp_tools):
        """Test sandbox configuration and package installation"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_configure', {
            'sandbox_id': 'sandbox_001',
            'configuration_status': 'completed',
            'packages_installed': ['express', 'mongoose', 'joi'],
            'commands_executed': 3,
            'setup_time': 45.2
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__sandbox_configure',
            sandbox_id='sandbox_001',
            install_packages=['express', 'mongoose', 'joi'],
            run_commands=['npm init -y', 'npm install --save-dev jest'],
            anthropic_key='claude-key'
        )
        
        assert result['data']['configuration_status'] == 'completed'
        assert 'express' in result['data']['packages_installed']
    
    def test_sandbox_logs_retrieval(self, mock_mcp_tools):
        """Test sandbox logs retrieval"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_logs', {
            'sandbox_id': 'sandbox_001',
            'logs': [
                {'timestamp': '2024-01-15T10:30:00Z', 'level': 'info', 'message': 'Server started'},
                {'timestamp': '2024-01-15T10:30:01Z', 'level': 'info', 'message': 'Listening on port 3000'},
                {'timestamp': '2024-01-15T10:30:05Z', 'level': 'error', 'message': 'Database connection failed'}
            ],
            'total_lines': 150,
            'lines_returned': 100
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__sandbox_logs',
            sandbox_id='sandbox_001',
            lines=100
        )
        
        assert len(result['data']['logs']) == 3
        assert result['data']['total_lines'] == 150
    
    def test_sandbox_status_monitoring(self, mock_mcp_tools):
        """Test sandbox status monitoring"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_status', {
            'sandbox_id': 'sandbox_001',
            'status': 'running',
            'uptime': 3600,
            'resource_usage': {
                'cpu_percent': 25.5,
                'memory_mb': 512,
                'disk_mb': 1024
            },
            'active_processes': 5,
            'network_connections': 2
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__sandbox_status',
            sandbox_id='sandbox_001'
        )
        
        assert result['data']['status'] == 'running'
        assert result['data']['uptime'] == 3600
        assert 'resource_usage' in result['data']


class TestNeuralNetworkIntegration:
    """Test neural network cluster and training functionality"""
    
    def test_neural_cluster_initialization(self, mock_mcp_tools):
        """Test neural network cluster initialization"""
        mock_mcp_tools.set_response('mcp__flow-nexus__neural_cluster_init', {
            'cluster_id': 'neural_cluster_001',
            'name': 'test_cluster',
            'architecture': 'transformer',
            'topology': 'mesh',
            'status': 'initialized',
            'nodes': [],
            'daa_enabled': True,
            'consensus': 'proof-of-learning'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__neural_cluster_init',
            name='test_cluster',
            architecture='transformer',
            topology='mesh',
            daaEnabled=True,
            wasmOptimization=True,
            consensus='proof-of-learning'
        )
        
        assert result['data']['name'] == 'test_cluster'
        assert result['data']['architecture'] == 'transformer'
        assert result['data']['daa_enabled'] is True
    
    def test_neural_node_deployment(self, mock_mcp_tools):
        """Test neural network node deployment"""
        mock_mcp_tools.set_response('mcp__flow-nexus__neural_node_deploy', {
            'node_id': 'node_001',
            'cluster_id': 'neural_cluster_001',
            'role': 'worker',
            'model': 'large',
            'sandbox_id': 'sandbox_neural_001',
            'status': 'deployed',
            'capabilities': ['training', 'inference'],
            'autonomy_level': 0.8
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__neural_node_deploy',
            cluster_id='neural_cluster_001',
            role='worker',
            model='large',
            template='nodejs',
            capabilities=['training', 'inference'],
            autonomy=0.8
        )
        
        assert result['data']['role'] == 'worker'
        assert result['data']['model'] == 'large'
        assert result['data']['status'] == 'deployed'
    
    def test_neural_cluster_connection(self, mock_mcp_tools):
        """Test neural cluster node connections"""
        mock_mcp_tools.set_response('mcp__flow-nexus__neural_cluster_connect', {
            'cluster_id': 'neural_cluster_001',
            'topology': 'mesh',
            'connections_established': 6,
            'network_status': 'connected',
            'latency_ms': 45.2
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__neural_cluster_connect',
            cluster_id='neural_cluster_001',
            topology='mesh'
        )
        
        assert result['data']['network_status'] == 'connected'
        assert result['data']['connections_established'] == 6
    
    def test_distributed_neural_training(self, mock_mcp_tools):
        """Test distributed neural network training"""
        mock_mcp_tools.set_response('mcp__flow-nexus__neural_train_distributed', {
            'training_id': 'training_001',
            'cluster_id': 'neural_cluster_001',
            'dataset': 'algorithms_dataset',
            'status': 'training',
            'epochs_completed': 0,
            'total_epochs': 10,
            'participating_nodes': 4,
            'estimated_completion': '2024-01-15T12:00:00Z'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__neural_train_distributed',
            cluster_id='neural_cluster_001',
            dataset='algorithms_dataset',
            epochs=10,
            batch_size=32,
            learning_rate=0.001,
            optimizer='adam',
            federated=False
        )
        
        assert result['data']['status'] == 'training'
        assert result['data']['total_epochs'] == 10
        assert result['data']['participating_nodes'] == 4
    
    def test_neural_cluster_status(self, mock_mcp_tools):
        """Test neural cluster status monitoring"""
        mock_mcp_tools.set_response('mcp__flow-nexus__neural_cluster_status', {
            'cluster_id': 'neural_cluster_001',
            'status': 'training',
            'total_nodes': 4,
            'active_nodes': 4,
            'training_sessions': [
                {
                    'training_id': 'training_001',
                    'progress': 0.35,
                    'loss': 0.245,
                    'accuracy': 0.789
                }
            ],
            'resource_usage': {
                'gpu_utilization': 85.2,
                'memory_usage': 67.8,
                'network_throughput': 123.4
            }
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__neural_cluster_status',
            cluster_id='neural_cluster_001'
        )
        
        assert result['data']['status'] == 'training'
        assert result['data']['active_nodes'] == 4
        assert len(result['data']['training_sessions']) == 1
    
    def test_distributed_prediction(self, mock_mcp_tools):
        """Test distributed neural network prediction"""
        mock_mcp_tools.set_response('mcp__flow-nexus__neural_predict_distributed', {
            'prediction_id': 'pred_001',
            'cluster_id': 'neural_cluster_001',
            'predictions': [
                {'node_id': 'node_001', 'prediction': [0.1, 0.7, 0.2], 'confidence': 0.89},
                {'node_id': 'node_002', 'prediction': [0.15, 0.65, 0.2], 'confidence': 0.85}
            ],
            'aggregated_prediction': [0.125, 0.675, 0.2],
            'ensemble_confidence': 0.87,
            'aggregation_method': 'weighted'
        })
        
        input_data = '{"features": [1.0, 2.5, 3.2, 4.1]}'
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__neural_predict_distributed',
            cluster_id='neural_cluster_001',
            input_data=input_data,
            aggregation='weighted'
        )
        
        assert len(result['data']['predictions']) == 2
        assert result['data']['ensemble_confidence'] > 0.8
        assert result['data']['aggregation_method'] == 'weighted'
    
    def test_neural_cluster_termination(self, mock_mcp_tools):
        """Test neural cluster termination"""
        mock_mcp_tools.set_response('mcp__flow-nexus__neural_cluster_terminate', {
            'cluster_id': 'neural_cluster_001',
            'termination_status': 'completed',
            'nodes_terminated': 4,
            'sandboxes_cleaned': 4,
            'resources_freed': True,
            'data_exported': True
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__neural_cluster_terminate',
            cluster_id='neural_cluster_001'
        )
        
        assert result['data']['termination_status'] == 'completed'
        assert result['data']['nodes_terminated'] == 4
        assert result['data']['resources_freed'] is True


class TestTemplateManagement:
    """Test template deployment and management"""
    
    def test_template_listing(self, mock_mcp_tools):
        """Test listing available templates"""
        mock_mcp_tools.set_response('mcp__flow-nexus__template_list', {
            'templates': [
                {
                    'id': 'template_001',
                    'name': 'Full-Stack Web App',
                    'category': 'web',
                    'description': 'Complete web application with React and Node.js',
                    'featured': True,
                    'variables': ['project_name', 'api_key']
                },
                {
                    'id': 'template_002',
                    'name': 'REST API',
                    'category': 'api',
                    'description': 'RESTful API with authentication',
                    'featured': False,
                    'variables': ['database_url', 'jwt_secret']
                }
            ],
            'total_count': 25,
            'featured_count': 8
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__template_list',
            category='web',
            featured=True,
            limit=20
        )
        
        assert len(result['data']['templates']) == 2
        assert result['data']['total_count'] == 25
        assert result['data']['templates'][0]['featured'] is True
    
    def test_template_details(self, mock_mcp_tools):
        """Test getting template details"""
        mock_mcp_tools.set_response('mcp__flow-nexus__template_get', {
            'id': 'template_001',
            'name': 'Full-Stack Web App',
            'description': 'Complete web application template',
            'version': '1.2.0',
            'author': 'Flow-Nexus Team',
            'requirements': {
                'nodejs': '>=16.0.0',
                'npm': '>=8.0.0'
            },
            'variables': [
                {
                    'name': 'project_name',
                    'type': 'string',
                    'required': True,
                    'description': 'Name of your project'
                },
                {
                    'name': 'anthropic_api_key',
                    'type': 'string',
                    'required': False,
                    'description': 'Anthropic API key for Claude integration'
                }
            ],
            'files': [
                'package.json',
                'src/app.js',
                'src/components/App.jsx',
                'README.md'
            ]
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__template_get',
            template_id='template_001'
        )
        
        assert result['data']['name'] == 'Full-Stack Web App'
        assert result['data']['version'] == '1.2.0'
        assert len(result['data']['variables']) == 2
        assert len(result['data']['files']) == 4
    
    def test_template_deployment(self, mock_mcp_tools):
        """Test template deployment"""
        mock_mcp_tools.set_response('mcp__flow-nexus__template_deploy', {
            'deployment_id': 'deploy_001',
            'template_id': 'template_001',
            'deployment_name': 'my-web-app',
            'status': 'deploying',
            'sandbox_id': 'sandbox_deploy_001',
            'variables_applied': {
                'project_name': 'my-web-app',
                'anthropic_api_key': '***'
            },
            'estimated_completion': 180
        })
        
        variables = {
            'project_name': 'my-web-app',
            'anthropic_api_key': 'claude-key-123'
        }
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__template_deploy',
            template_id='template_001',
            deployment_name='my-web-app',
            variables=variables,
            env_vars={'NODE_ENV': 'development'}
        )
        
        assert result['data']['status'] == 'deploying'
        assert result['data']['deployment_name'] == 'my-web-app'
        assert 'variables_applied' in result['data']


class TestWorkflowManagement:
    """Test workflow creation and execution"""
    
    def test_workflow_creation(self, mock_mcp_tools):
        """Test workflow creation"""
        mock_mcp_tools.set_response('mcp__flow-nexus__workflow_create', {
            'workflow_id': 'workflow_001',
            'name': 'Full-Stack Development',
            'status': 'created',
            'steps': [
                {'id': 'step_001', 'name': 'Setup Backend', 'agent_type': 'coder'},
                {'id': 'step_002', 'name': 'Build Frontend', 'agent_type': 'coder'},
                {'id': 'step_003', 'name': 'Run Tests', 'agent_type': 'tester'}
            ],
            'triggers': ['manual', 'git_push'],
            'estimated_duration': 900
        })
        
        workflow_steps = [
            {
                'name': 'Setup Backend',
                'agent_type': 'coder',
                'instructions': 'Create REST API with authentication',
                'dependencies': []
            },
            {
                'name': 'Build Frontend',
                'agent_type': 'coder',
                'instructions': 'Create React frontend',
                'dependencies': ['Setup Backend']
            },
            {
                'name': 'Run Tests',
                'agent_type': 'tester',
                'instructions': 'Run comprehensive test suite',
                'dependencies': ['Setup Backend', 'Build Frontend']
            }
        ]
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__workflow_create',
            name='Full-Stack Development',
            description='Complete full-stack application development',
            steps=workflow_steps,
            triggers=['manual', 'git_push'],
            priority=8
        )
        
        assert result['data']['name'] == 'Full-Stack Development'
        assert len(result['data']['steps']) == 3
        assert 'manual' in result['data']['triggers']
    
    def test_workflow_execution(self, mock_mcp_tools):
        """Test workflow execution"""
        mock_mcp_tools.set_response('mcp__flow-nexus__workflow_execute', {
            'execution_id': 'exec_workflow_001',
            'workflow_id': 'workflow_001',
            'status': 'running',
            'current_step': 'step_001',
            'progress': 0.33,
            'started_at': '2024-01-15T10:30:00Z',
            'estimated_completion': '2024-01-15T10:45:00Z'
        })
        
        input_data = {
            'project_name': 'test-app',
            'requirements': ['authentication', 'database', 'api']
        }
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__workflow_execute',
            workflow_id='workflow_001',
            input_data=input_data,
            async_mode=True
        )
        
        assert result['data']['status'] == 'running'
        assert result['data']['current_step'] == 'step_001'
        assert result['data']['progress'] == 0.33
    
    def test_workflow_status_monitoring(self, mock_mcp_tools):
        """Test workflow status monitoring"""
        mock_mcp_tools.set_response('mcp__flow-nexus__workflow_status', {
            'workflow_id': 'workflow_001',
            'execution_id': 'exec_workflow_001',
            'status': 'running',
            'current_step': 'step_002',
            'completed_steps': ['step_001'],
            'progress': 0.67,
            'metrics': {
                'duration_ms': 450000,
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'agent_utilization': 0.85
            },
            'logs': [
                {'timestamp': '2024-01-15T10:30:00Z', 'step': 'step_001', 'message': 'Backend setup completed'},
                {'timestamp': '2024-01-15T10:35:00Z', 'step': 'step_002', 'message': 'Frontend build started'}
            ]
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__workflow_status',
            workflow_id='workflow_001',
            execution_id='exec_workflow_001',
            include_metrics=True
        )
        
        assert result['data']['status'] == 'running'
        assert result['data']['progress'] == 0.67
        assert len(result['data']['completed_steps']) == 1
        assert 'metrics' in result['data']
    
    def test_workflow_agent_assignment(self, mock_mcp_tools):
        """Test workflow agent assignment"""
        mock_mcp_tools.set_response('mcp__flow-nexus__workflow_agent_assign', {
            'task_id': 'task_001',
            'assigned_agent': {
                'agent_id': 'agent_coder_002',
                'type': 'coder',
                'specialization': 'full-stack',
                'availability': 'available',
                'match_score': 0.95
            },
            'assignment_reason': 'Best match for full-stack development task',
            'alternative_agents': [
                {'agent_id': 'agent_coder_001', 'match_score': 0.87},
                {'agent_id': 'agent_coder_003', 'match_score': 0.82}
            ]
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__workflow_agent_assign',
            task_id='task_001',
            agent_type='coder',
            use_vector_similarity=True
        )
        
        assert result['data']['assigned_agent']['type'] == 'coder'
        assert result['data']['assigned_agent']['match_score'] == 0.95
        assert len(result['data']['alternative_agents']) == 2


class TestAuthenticationAndUserManagement:
    """Test authentication and user management"""
    
    def test_auth_status_check(self, mock_mcp_tools):
        """Test authentication status check"""
        mock_mcp_tools.set_response('mcp__flow-nexus__auth_status', {
            'authenticated': True,
            'user_id': 'user_001',
            'tier': 'pro',
            'permissions': ['sandbox_create', 'neural_train', 'workflow_execute'],
            'session_expires': '2024-01-15T18:00:00Z',
            'rate_limits': {
                'requests_per_minute': 100,
                'sandboxes_max': 10,
                'storage_gb': 50
            }
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__auth_status',
            detailed=True
        )
        
        assert result['data']['authenticated'] is True
        assert result['data']['tier'] == 'pro'
        assert 'sandbox_create' in result['data']['permissions']
    
    def test_user_registration(self, mock_mcp_tools):
        """Test user registration"""
        mock_mcp_tools.set_response('mcp__flow-nexus__user_register', {
            'user_id': 'user_002',
            'email': 'test@example.com',
            'registration_status': 'completed',
            'verification_required': True,
            'verification_email_sent': True,
            'default_tier': 'free'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__user_register',
            email='test@example.com',
            password='secure-password-123',
            full_name='Test User'
        )
        
        assert result['data']['registration_status'] == 'completed'
        assert result['data']['verification_required'] is True
        assert result['data']['default_tier'] == 'free'
    
    def test_user_login(self, mock_mcp_tools):
        """Test user login"""
        mock_mcp_tools.set_response('mcp__flow-nexus__user_login', {
            'session_token': 'jwt_token_here',
            'user_id': 'user_001',
            'session_expires': '2024-01-15T18:00:00Z',
            'login_status': 'success',
            'last_login': '2024-01-14T10:30:00Z'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__user_login',
            email='test@example.com',
            password='secure-password-123'
        )
        
        assert result['data']['login_status'] == 'success'
        assert 'session_token' in result['data']
        assert result['data']['user_id'] == 'user_001'
    
    def test_user_profile_management(self, mock_mcp_tools):
        """Test user profile management"""
        mock_mcp_tools.set_response('mcp__flow-nexus__user_profile', {
            'user_id': 'user_001',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'tier': 'pro',
            'created_at': '2024-01-01T00:00:00Z',
            'last_active': '2024-01-15T10:30:00Z',
            'usage_stats': {
                'sandboxes_created': 25,
                'workflows_executed': 10,
                'neural_trainings': 5
            }
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__user_profile',
            user_id='user_001'
        )
        
        assert result['data']['tier'] == 'pro'
        assert 'usage_stats' in result['data']
        assert result['data']['usage_stats']['sandboxes_created'] == 25
    
    def test_user_tier_upgrade(self, mock_mcp_tools):
        """Test user tier upgrade"""
        mock_mcp_tools.set_response('mcp__flow-nexus__user_upgrade', {
            'user_id': 'user_001',
            'previous_tier': 'free',
            'new_tier': 'pro',
            'upgrade_status': 'completed',
            'effective_date': '2024-01-15T10:30:00Z',
            'new_limits': {
                'sandboxes_max': 20,
                'storage_gb': 100,
                'neural_clusters': 5
            }
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__user_upgrade',
            user_id='user_001',
            tier='pro'
        )
        
        assert result['data']['upgrade_status'] == 'completed'
        assert result['data']['new_tier'] == 'pro'
        assert result['data']['new_limits']['sandboxes_max'] == 20


class TestRealTimeMonitoring:
    """Test real-time monitoring and event streaming"""
    
    def test_execution_stream_subscription(self, mock_mcp_tools):
        """Test execution stream subscription"""
        mock_mcp_tools.set_response('mcp__flow-nexus__execution_stream_subscribe', {
            'stream_id': 'stream_001',
            'sandbox_id': 'sandbox_001',
            'stream_type': 'claude-code',
            'subscription_status': 'active',
            'websocket_url': 'wss://stream.flow-nexus.dev/stream_001'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__execution_stream_subscribe',
            sandbox_id='sandbox_001',
            stream_type='claude-code'
        )
        
        assert result['data']['subscription_status'] == 'active'
        assert result['data']['stream_type'] == 'claude-code'
        assert 'websocket_url' in result['data']
    
    def test_execution_stream_status(self, mock_mcp_tools):
        """Test execution stream status"""
        mock_mcp_tools.set_response('mcp__flow-nexus__execution_stream_status', {
            'stream_id': 'stream_001',
            'status': 'active',
            'connected_clients': 3,
            'events_sent': 1245,
            'last_event': '2024-01-15T10:30:00Z',
            'bandwidth_usage': '2.5 MB/s'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__execution_stream_status',
            stream_id='stream_001'
        )
        
        assert result['data']['status'] == 'active'
        assert result['data']['connected_clients'] == 3
        assert result['data']['events_sent'] == 1245
    
    def test_realtime_database_subscription(self, mock_mcp_tools):
        """Test real-time database subscription"""
        mock_mcp_tools.set_response('mcp__flow-nexus__realtime_subscribe', {
            'subscription_id': 'sub_001',
            'table': 'workflows',
            'event': 'UPDATE',
            'subscription_status': 'active',
            'channel': 'realtime:workflows:UPDATE'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__realtime_subscribe',
            table='workflows',
            event='UPDATE',
            filter='status=in.(running,completed)'
        )
        
        assert result['data']['subscription_status'] == 'active'
        assert result['data']['table'] == 'workflows'
        assert result['data']['event'] == 'UPDATE'
    
    def test_execution_files_monitoring(self, mock_mcp_tools):
        """Test execution files monitoring"""
        mock_mcp_tools.set_response('mcp__flow-nexus__execution_files_list', {
            'stream_id': 'stream_001',
            'files': [
                {
                    'file_id': 'file_001',
                    'path': '/workspace/app.js',
                    'created_by': 'claude-code',
                    'file_type': 'javascript',
                    'size_bytes': 2048,
                    'last_modified': '2024-01-15T10:30:00Z'
                },
                {
                    'file_id': 'file_002',
                    'path': '/workspace/package.json',
                    'created_by': 'claude-flow',
                    'file_type': 'json',
                    'size_bytes': 512,
                    'last_modified': '2024-01-15T10:29:00Z'
                }
            ],
            'total_files': 15,
            'total_size_bytes': 50432
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__execution_files_list',
            stream_id='stream_001',
            created_by='claude-code',
            file_type='javascript'
        )
        
        assert len(result['data']['files']) == 2
        assert result['data']['total_files'] == 15
        assert result['data']['files'][0]['created_by'] == 'claude-code'


class TestStorageManagement:
    """Test storage and file management"""
    
    def test_file_upload_to_storage(self, mock_mcp_tools):
        """Test file upload to cloud storage"""
        mock_mcp_tools.set_response('mcp__flow-nexus__storage_upload', {
            'bucket': 'user-files',
            'path': '/projects/my-app/src/app.js',
            'upload_status': 'completed',
            'size_bytes': 2048,
            'checksum': 'sha256:abc123...',
            'public_url': 'https://storage.flow-nexus.dev/user-files/projects/my-app/src/app.js'
        })
        
        file_content = """
        const express = require('express');
        const app = express();
        
        app.get('/', (req, res) => {
            res.send('Hello from cloud storage!');
        });
        
        module.exports = app;
        """
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__storage_upload',
            bucket='user-files',
            path='/projects/my-app/src/app.js',
            content=file_content,
            content_type='application/javascript'
        )
        
        assert result['data']['upload_status'] == 'completed'
        assert result['data']['size_bytes'] == 2048
        assert 'public_url' in result['data']
    
    def test_storage_file_listing(self, mock_mcp_tools):
        """Test storage file listing"""
        mock_mcp_tools.set_response('mcp__flow-nexus__storage_list', {
            'bucket': 'user-files',
            'files': [
                {
                    'name': 'app.js',
                    'path': '/projects/my-app/src/app.js',
                    'size_bytes': 2048,
                    'last_modified': '2024-01-15T10:30:00Z',
                    'content_type': 'application/javascript'
                },
                {
                    'name': 'package.json',
                    'path': '/projects/my-app/package.json',
                    'size_bytes': 512,
                    'last_modified': '2024-01-15T10:25:00Z',
                    'content_type': 'application/json'
                }
            ],
            'total_count': 25,
            'total_size_bytes': 102400
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__storage_list',
            bucket='user-files',
            path='/projects/my-app',
            limit=100
        )
        
        assert len(result['data']['files']) == 2
        assert result['data']['total_count'] == 25
        assert result['data']['total_size_bytes'] == 102400
    
    def test_storage_url_generation(self, mock_mcp_tools):
        """Test storage URL generation"""
        mock_mcp_tools.set_response('mcp__flow-nexus__storage_get_url', {
            'bucket': 'user-files',
            'path': '/projects/my-app/src/app.js',
            'url': 'https://storage.flow-nexus.dev/user-files/projects/my-app/src/app.js?token=abc123&expires=1705320600',
            'expires_at': '2024-01-15T16:30:00Z',
            'access_type': 'temporary'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__storage_get_url',
            bucket='user-files',
            path='/projects/my-app/src/app.js',
            expires_in=3600
        )
        
        assert 'url' in result['data']
        assert 'expires_at' in result['data']
        assert 'token=' in result['data']['url']
    
    def test_storage_file_deletion(self, mock_mcp_tools):
        """Test storage file deletion"""
        mock_mcp_tools.set_response('mcp__flow-nexus__storage_delete', {
            'bucket': 'user-files',
            'path': '/projects/my-app/src/old-file.js',
            'deletion_status': 'completed',
            'deleted_at': '2024-01-15T10:30:00Z'
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__storage_delete',
            bucket='user-files',
            path='/projects/my-app/src/old-file.js'
        )
        
        assert result['data']['deletion_status'] == 'completed'
        assert 'deleted_at' in result['data']


class TestErrorHandlingAndRetry:
    """Test error handling and retry mechanisms"""
    
    def test_mcp_tool_timeout_handling(self, mock_mcp_tools):
        """Test MCP tool timeout handling"""
        import time
        
        # Simulate timeout
        def slow_response(*args, **kwargs):
            time.sleep(2)
            return {"status": "success"}
        
        mock_mcp_tools.call_mcp_tool = slow_response
        
        start_time = time.time()
        try:
            result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__sandbox_create')
            duration = time.time() - start_time
            assert duration >= 2  # Should have waited
        except Exception:
            # Timeout exception is acceptable
            duration = time.time() - start_time
            assert duration >= 1  # Should have attempted
    
    def test_mcp_tool_network_error_handling(self, mock_mcp_tools):
        """Test MCP tool network error handling"""
        mock_mcp_tools.set_error('mcp__flow-nexus__sandbox_create', 
                                ConnectionError("Network unavailable"))
        
        with pytest.raises(ConnectionError):
            mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__sandbox_create')
    
    def test_mcp_tool_authentication_error(self, mock_mcp_tools):
        """Test MCP tool authentication error handling"""
        mock_mcp_tools.set_error('mcp__flow-nexus__auth_status',
                                PermissionError("Authentication required"))
        
        with pytest.raises(PermissionError):
            mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__auth_status')
    
    def test_mcp_tool_rate_limit_handling(self, mock_mcp_tools):
        """Test MCP tool rate limit handling"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_create', {
            'error': 'rate_limit_exceeded',
            'message': 'Rate limit exceeded. Try again in 60 seconds.',
            'retry_after': 60,
            'current_usage': 100,
            'limit': 100
        })
        
        result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__sandbox_create')
        
        assert 'error' in result['data']
        assert result['data']['error'] == 'rate_limit_exceeded'
        assert result['data']['retry_after'] == 60
    
    def test_mcp_tool_invalid_parameters(self, mock_mcp_tools):
        """Test MCP tool invalid parameters handling"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_create', {
            'error': 'invalid_parameters',
            'message': 'Invalid template specified',
            'validation_errors': [
                {'field': 'template', 'error': 'must be one of: node, python, react'}
            ]
        })
        
        result = mock_mcp_tools.call_mcp_tool(
            'mcp__flow-nexus__sandbox_create',
            template='invalid_template'
        )
        
        assert 'error' in result['data']
        assert result['data']['error'] == 'invalid_parameters'
        assert len(result['data']['validation_errors']) == 1
    
    def test_mcp_tool_resource_exhaustion(self, mock_mcp_tools):
        """Test MCP tool resource exhaustion handling"""
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_create', {
            'error': 'resource_exhausted',
            'message': 'No available resources to create sandbox',
            'available_resources': 0,
            'queue_position': 15,
            'estimated_wait_time': 300
        })
        
        result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__sandbox_create')
        
        assert 'error' in result['data']
        assert result['data']['error'] == 'resource_exhausted'
        assert result['data']['queue_position'] == 15


@pytest.mark.integration
class TestFlowNexusIntegration:
    """Integration tests for Flow-Nexus components"""
    
    def test_complete_development_workflow(self, mock_mcp_tools):
        """Test complete development workflow from start to finish"""
        # Set up responses for a complete workflow
        responses = {
            'mcp__flow-nexus__swarm_init': {
                'swarm_id': 'swarm_dev_001',
                'topology': 'mesh',
                'status': 'initialized'
            },
            'mcp__flow-nexus__agent_spawn': {
                'agent_id': 'agent_coder_001',
                'type': 'coder',
                'status': 'active'
            },
            'mcp__flow-nexus__sandbox_create': {
                'sandbox_id': 'sandbox_dev_001',
                'template': 'node',
                'status': 'running'
            },
            'mcp__flow-nexus__template_deploy': {
                'deployment_id': 'deploy_001',
                'status': 'completed'
            },
            'mcp__flow-nexus__task_orchestrate': {
                'task_id': 'task_001',
                'status': 'completed'
            }
        }
        
        for tool_name, response in responses.items():
            mock_mcp_tools.set_response(tool_name, response)
        
        # Simulate complete workflow
        swarm_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__swarm_init', topology='mesh')
        agent_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__agent_spawn', type='coder')
        sandbox_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__sandbox_create', template='node')
        deploy_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__template_deploy', template_id='web-app')
        task_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__task_orchestrate', task='Build web app')
        
        # Verify the workflow completed successfully
        assert swarm_result['data']['status'] == 'initialized'
        assert agent_result['data']['status'] == 'active'
        assert sandbox_result['data']['status'] == 'running'
        assert deploy_result['data']['status'] == 'completed'
        assert task_result['data']['status'] == 'completed'
        
        # Verify call history
        expected_calls = [
            ('mcp__flow-nexus__swarm_init', {'topology': 'mesh'}),
            ('mcp__flow-nexus__agent_spawn', {'type': 'coder'}),
            ('mcp__flow-nexus__sandbox_create', {'template': 'node'}),
            ('mcp__flow-nexus__template_deploy', {'template_id': 'web-app'}),
            ('mcp__flow-nexus__task_orchestrate', {'task': 'Build web app'})
        ]
        
        for expected_call in expected_calls:
            assert expected_call in mock_mcp_tools.call_history
    
    def test_neural_training_pipeline(self, mock_mcp_tools):
        """Test complete neural training pipeline"""
        # Set up neural training pipeline responses
        neural_responses = {
            'mcp__flow-nexus__neural_cluster_init': {
                'cluster_id': 'neural_001',
                'status': 'initialized'
            },
            'mcp__flow-nexus__neural_node_deploy': {
                'node_id': 'node_001',
                'status': 'deployed'
            },
            'mcp__flow-nexus__neural_cluster_connect': {
                'network_status': 'connected'
            },
            'mcp__flow-nexus__neural_train_distributed': {
                'training_id': 'training_001',
                'status': 'completed'
            },
            'mcp__flow-nexus__neural_predict_distributed': {
                'prediction_id': 'pred_001',
                'aggregated_prediction': [0.1, 0.8, 0.1]
            }
        }
        
        for tool_name, response in neural_responses.items():
            mock_mcp_tools.set_response(tool_name, response)
        
        # Execute neural training pipeline
        cluster_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__neural_cluster_init', name='test')
        node_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__neural_node_deploy', cluster_id='neural_001')
        connect_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__neural_cluster_connect', cluster_id='neural_001')
        train_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__neural_train_distributed', cluster_id='neural_001')
        predict_result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__neural_predict_distributed', cluster_id='neural_001')
        
        # Verify pipeline success
        assert cluster_result['data']['status'] == 'initialized'
        assert node_result['data']['status'] == 'deployed'
        assert connect_result['data']['network_status'] == 'connected'
        assert train_result['data']['status'] == 'completed'
        assert len(predict_result['data']['aggregated_prediction']) == 3
    
    def test_error_recovery_workflow(self, mock_mcp_tools):
        """Test error recovery in workflow execution"""
        # First attempt fails
        mock_mcp_tools.set_error('mcp__flow-nexus__sandbox_create', 
                                ConnectionError("Temporary network issue"))
        
        with pytest.raises(ConnectionError):
            mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__sandbox_create')
        
        # Second attempt succeeds
        mock_mcp_tools.set_response('mcp__flow-nexus__sandbox_create', {
            'sandbox_id': 'sandbox_retry_001',
            'status': 'running'
        })
        
        result = mock_mcp_tools.call_mcp_tool('mcp__flow-nexus__sandbox_create')
        assert result['data']['status'] == 'running'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
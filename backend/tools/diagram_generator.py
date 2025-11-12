"""
Diagram Generator Tool
Supports Mermaid diagrams, PlantUML, and other diagram types
"""
import os
import base64
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
import aiohttp


class DiagramGenerator:
    """Generate diagrams using various diagram description languages"""
    
    # Kroki service for rendering diagrams
    KROKI_URL = "https://kroki.io"
    
    # Supported diagram types
    DIAGRAM_TYPES = {
        'mermaid': {
            'name': 'Mermaid',
            'description': 'Flowcharts, sequence diagrams, gantt charts',
            'formats': ['svg', 'png']
        },
        'plantuml': {
            'name': 'PlantUML',
            'description': 'UML diagrams (class, sequence, activity, etc.)',
            'formats': ['svg', 'png']
        },
        'graphviz': {
            'name': 'Graphviz',
            'description': 'Graph visualization',
            'formats': ['svg', 'png']
        },
        'blockdiag': {
            'name': 'BlockDiag',
            'description': 'Simple block diagrams',
            'formats': ['svg', 'png']
        },
        'bpmn': {
            'name': 'BPMN',
            'description': 'Business Process Model diagrams',
            'formats': ['svg', 'png']
        },
        'excalidraw': {
            'name': 'Excalidraw',
            'description': 'Hand-drawn style diagrams',
            'formats': ['svg', 'png']
        }
    }
    
    def __init__(self, output_dir: str = "output/diagrams"):
        """
        Initialize diagram generator
        
        Args:
            output_dir: Directory to save generated diagrams
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, diagram_code: str, diagram_type: str, format: str) -> Path:
        """
        Get cache file path for a diagram
        
        Args:
            diagram_code: Diagram source code
            diagram_type: Type of diagram
            format: Output format
        
        Returns:
            Path to cache file
        """
        # Create hash of diagram code for caching
        code_hash = hashlib.md5(diagram_code.encode()).hexdigest()[:12]
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{diagram_type}_{timestamp}_{code_hash}.{format}"
        return self.output_dir / filename
    
    async def generate_diagram_async(
        self,
        diagram_code: str,
        diagram_type: str = 'mermaid',
        output_format: str = 'svg'
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate diagram using Kroki service (async)
        
        Args:
            diagram_code: Diagram source code
            diagram_type: Type of diagram (mermaid, plantuml, etc.)
            output_format: Output format (svg, png)
        
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            # Check cache first
            cache_path = self._get_cache_path(diagram_code, diagram_type, output_format)
            if cache_path.exists():
                return True, str(cache_path), None
            
            # Use POST request with JSON payload (more reliable than GET with base64 URL)
            url = f"{self.KROKI_URL}/{diagram_type}/{output_format}"
            
            # Prepare JSON payload
            payload = {
                "diagram_source": diagram_code
            }
            
            # Make async request to Kroki
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # Save to file
                        with open(cache_path, 'wb') as f:
                            f.write(content)
                        
                        return True, str(cache_path), None
                    else:
                        error_text = await response.text()
                        return False, None, f"Kroki error (HTTP {response.status}): {error_text}"
        
        except asyncio.TimeoutError:
            return False, None, "Request timeout - diagram generation took too long"
        except Exception as e:
            return False, None, f"Error generating diagram: {str(e)}"
    
    def generate_diagram(
        self,
        diagram_code: str,
        diagram_type: str = 'mermaid',
        output_format: str = 'svg'
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate diagram (sync wrapper)
        
        Args:
            diagram_code: Diagram source code
            diagram_type: Type of diagram
            output_format: Output format
        
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.generate_diagram_async(diagram_code, diagram_type, output_format)
        )
    
    def validate_diagram_code(
        self,
        diagram_code: str,
        diagram_type: str = 'mermaid'
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate diagram code syntax
        
        Args:
            diagram_code: Diagram source code
            diagram_type: Type of diagram
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not diagram_code or not diagram_code.strip():
            return False, "Diagram code cannot be empty"
        
        if diagram_type not in self.DIAGRAM_TYPES:
            return False, f"Unsupported diagram type: {diagram_type}"
        
        # Basic validation based on diagram type
        if diagram_type == 'mermaid':
            # Check for common Mermaid keywords
            valid_starts = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 
                          'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey']
            if not any(diagram_code.strip().startswith(keyword) for keyword in valid_starts):
                return False, "Mermaid diagram must start with a valid diagram type (graph, sequenceDiagram, etc.)"
        
        elif diagram_type == 'plantuml':
            # Check for PlantUML tags
            if '@startuml' not in diagram_code or '@enduml' not in diagram_code:
                return False, "PlantUML diagram must be wrapped in @startuml...@enduml tags"
        
        return True, None
    
    def get_diagram_templates(self) -> Dict[str, Dict[str, str]]:
        """
        Get pre-defined diagram templates
        
        Returns:
            Dictionary of template categories and their templates
        """
        return {
            'mermaid_flowchart': {
                'name': 'Mermaid Flowchart',
                'description': 'Basic flowchart with decision points',
                'type': 'mermaid',
                'code': '''flowchart TD
    Start([Start]) --> Input[/Input Data/]
    Input --> Process[Process Data]
    Process --> Decision{Valid?}
    Decision -->|Yes| Output[/Output Result/]
    Decision -->|No| Error[Show Error]
    Error --> Input
    Output --> End([End])'''
            },
            'mermaid_sequence': {
                'name': 'Mermaid Sequence Diagram',
                'description': 'Sequence diagram for API interactions',
                'type': 'mermaid',
                'code': '''sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database
    
    User->>Frontend: Enter credentials
    Frontend->>Backend: POST /login
    Backend->>Database: Query user
    Database-->>Backend: User data
    Backend-->>Frontend: Auth token
    Frontend-->>User: Welcome message'''
            },
            'mermaid_class': {
                'name': 'Mermaid Class Diagram',
                'description': 'Class diagram showing relationships',
                'type': 'mermaid',
                'code': '''classDiagram
    class User {
        +int id
        +string username
        +string email
        +login()
        +logout()
    }
    
    class Post {
        +int id
        +string title
        +string content
        +Date created_at
        +publish()
    }
    
    class Comment {
        +int id
        +string text
        +Date created_at
    }
    
    User "1" --> "*" Post : creates
    Post "1" --> "*" Comment : has'''
            },
            'mermaid_gantt': {
                'name': 'Mermaid Gantt Chart',
                'description': 'Project timeline visualization',
                'type': 'mermaid',
                'code': '''gantt
    title Project Development Timeline
    dateFormat YYYY-MM-DD
    
    section Planning
    Requirements gathering    :a1, 2024-01-01, 7d
    Design phase             :a2, after a1, 7d
    
    section Development
    Backend development      :b1, after a2, 14d
    Frontend development     :b2, after a2, 14d
    Testing                  :b3, after b1, 7d
    
    section Deployment
    Deployment               :c1, after b3, 3d
    Documentation            :c2, after b3, 5d'''
            },
            'mermaid_state': {
                'name': 'Mermaid State Diagram',
                'description': 'State machine visualization',
                'type': 'mermaid',
                'code': '''stateDiagram-v2
    [*] --> Idle
    Idle --> Loading: Start Request
    Loading --> Success: Data Received
    Loading --> Error: Request Failed
    Success --> Idle: Reset
    Error --> Idle: Retry
    Error --> [*]: Give Up'''
            },
            'mermaid_er': {
                'name': 'Mermaid ER Diagram',
                'description': 'Entity-relationship database schema',
                'type': 'mermaid',
                'code': '''erDiagram
    USER ||--o{ ORDER : places
    USER {
        int id PK
        string username
        string email
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        int id PK
        date order_date
        int user_id FK
    }
    PRODUCT ||--o{ ORDER_ITEM : "ordered in"
    PRODUCT {
        int id PK
        string name
        float price
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int quantity
    }'''
            },
            'plantuml_class': {
                'name': 'PlantUML Class Diagram',
                'description': 'Detailed UML class diagram',
                'type': 'plantuml',
                'code': '''@startuml
class Vehicle {
  + brand: String
  + model: String
  + year: int
  + start(): void
  + stop(): void
}

class Car extends Vehicle {
  + numDoors: int
  + openTrunk(): void
}

class Motorcycle extends Vehicle {
  + hasSidecar: boolean
  + wheelie(): void
}

Vehicle <|-- Car
Vehicle <|-- Motorcycle
@enduml'''
            },
            'plantuml_sequence': {
                'name': 'PlantUML Sequence Diagram',
                'description': 'Detailed sequence interactions',
                'type': 'plantuml',
                'code': '''@startuml
actor User
participant "Web App" as Web
participant "API Server" as API
database Database

User -> Web: Click Login
activate Web
Web -> API: POST /auth/login
activate API

API -> Database: SELECT user
activate Database
Database --> API: User record
deactivate Database

alt Credentials Valid
    API --> Web: JWT Token
    Web --> User: Redirect to Dashboard
else Invalid Credentials
    API --> Web: 401 Error
    Web --> User: Show error message
end

deactivate API
deactivate Web
@enduml'''
            },
            'plantuml_activity': {
                'name': 'PlantUML Activity Diagram',
                'description': 'Business process flow',
                'type': 'plantuml',
                'code': '''@startuml
start
:User submits form;
if (Data valid?) then (yes)
  :Save to database;
  :Send confirmation email;
  if (Email sent?) then (yes)
    :Show success message;
  else (no)
    :Log email error;
    :Show partial success;
  endif
else (no)
  :Show validation errors;
  stop
endif
:Redirect to dashboard;
stop
@enduml'''
            },
            'plantuml_usecase': {
                'name': 'PlantUML Use Case Diagram',
                'description': 'System use case overview',
                'type': 'plantuml',
                'code': '''@startuml
left to right direction
actor User
actor Admin

rectangle "E-Commerce System" {
  usecase "Browse Products" as UC1
  usecase "Add to Cart" as UC2
  usecase "Checkout" as UC3
  usecase "Manage Products" as UC4
  usecase "View Reports" as UC5
  
  User --> UC1
  User --> UC2
  User --> UC3
  Admin --> UC4
  Admin --> UC5
  
  UC3 .> UC2 : includes
  UC2 .> UC1 : includes
}
@enduml'''
            },
            'graphviz_directed': {
                'name': 'Graphviz Directed Graph',
                'description': 'Directed graph visualization',
                'type': 'graphviz',
                'code': '''digraph G {
  rankdir=LR;
  node [shape=box, style=rounded];
  
  A [label="Start"];
  B [label="Process 1"];
  C [label="Process 2"];
  D [label="Decision"];
  E [label="Output"];
  F [label="End"];
  
  A -> B;
  B -> C;
  C -> D;
  D -> E [label="Yes"];
  D -> B [label="No"];
  E -> F;
}'''
            }
        }
    
    def list_diagram_types(self) -> List[Dict[str, str]]:
        """
        List all supported diagram types
        
        Returns:
            List of diagram type information
        """
        return [
            {
                'id': type_id,
                'name': info['name'],
                'description': info['description'],
                'formats': info['formats']
            }
            for type_id, info in self.DIAGRAM_TYPES.items()
        ]
    
    def export_diagram(
        self,
        diagram_code: str,
        diagram_type: str,
        formats: List[str] = ['svg', 'png']
    ) -> Dict[str, Optional[str]]:
        """
        Export diagram in multiple formats
        
        Args:
            diagram_code: Diagram source code
            diagram_type: Type of diagram
            formats: List of formats to export
        
        Returns:
            Dictionary mapping format to file path
        """
        results = {}
        
        for fmt in formats:
            success, file_path, error = self.generate_diagram(
                diagram_code, diagram_type, fmt
            )
            results[fmt] = file_path if success else None
        
        return results
    
    def get_diagram_info(self, file_path: str) -> Optional[Dict[str, any]]:
        """
        Get information about a generated diagram
        
        Args:
            file_path: Path to diagram file
        
        Returns:
            Diagram metadata or None
        """
        path = Path(file_path)
        if not path.exists():
            return None
        
        return {
            'filename': path.name,
            'format': path.suffix[1:],
            'size_bytes': path.stat().st_size,
            'size_kb': round(path.stat().st_size / 1024, 2),
            'created': datetime.fromtimestamp(path.stat().st_ctime),
            'path': str(path)
        }


# Global instance
diagram_generator = DiagramGenerator()


import inspect
from typing import List, Callable

def create_function_tool(func: Callable) -> dict:
    """
    Create a function tool requirement dictionary for a given function.
    
    Args:
    func (callable): The function to create a tool requirement for.
    
    Returns:
    dict: A dictionary representing the function tool requirement.
    """
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    
    parameters = {}
    required = []
    
    for name, param in signature.parameters.items():
        param_info = {
            "type": "string",  # Default to string, adjust as needed
            "description": f"Parameter: {name}"
        }
        
        if param.default == inspect.Parameter.empty:
            required.append(name)
        
        parameters[name] = param_info
    
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": docstring.split('\n')[0] if docstring else "No description provided",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

def create_multiple_function_tools(functions: List[Callable]) -> List[dict]:
    """
    Create function tool requirements for multiple functions.
    
    Args:
    functions (List[Callable]): A list of functions to create tool requirements for.
    
    Returns:
    List[dict]: A list of dictionaries, each representing a function tool requirement.
    """
    return [create_function_tool(func) for func in functions]

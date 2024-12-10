def extract_values(data):
    try:
        # Check if data exists and has 'issues' key
        if not data or not isinstance(data, dict):
            return {'error': 'Invalid data format', 'data': []}
            
        issues = data.get('issues', [])
        if not issues:
            return {'error': 'No issues found', 'data': []}

        result = []
        for index, issue in enumerate(issues):
            try:
                # Use get() method with default values to handle missing keys
                issue_data = {
                    'id': issue.get('id', 'N/A'),
                    'status_name': (
                        issue.get('fields', {})
                        .get('status', {})
                        .get('name', 'N/A')
                    )
                }
                result.append(issue_data)
            except Exception as e:
                # Handle errors for individual records without failing the entire process
                print(f"Warning: Error processing issue at index {index}: {str(e)}")
                result.append({
                    'id': 'ERROR',
                    'status_name': 'ERROR',
                    'error': str(e)
                })

        return {'error': None, 'data': result}

    except Exception as e:
        return {'error': f"Fatal error: {str(e)}", 'data': []}

# Example usage:
# response = extract_values(data)
# if response['error']:
#     print(f"Error occurred: {response['error']}")
# else:
#     for item in response['data']:
#         print(item)

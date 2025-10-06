def global_context(request):
    return {
        "status": {
            "info": "primary",
            "success": "success",
            "error": "danger",
        },
        "icons": {
            "info": "bi-info-circle",
            "success": "bi-check-circle",
            "error": "bi-exclamation-triangle",
        }
    }

from db import DatabaseConnection

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from project.server.auth.helpers import token_required, admin_required, current_identity
from project.server.validation.validators import valid_create_data, wrong_status_data
from flasgger import swag_from

interventions_blueprint = Blueprint('interventions', __name__, url_prefix="/api/v2")

db_name = DatabaseConnection()


class GetInterventionsAPI(MethodView):
    """
    Intervention resource
    """
    @token_required
    @swag_from('../docs/get_intervention.yml')
    def get(self):
        """
        get interventions
        """
        interventions = db_name.get_incidents('intervention')
        if not interventions:
            return jsonify({
                'error': 'There are no interventions',
                'status': 404
            })

        responseObject = ({
            "status": 200,
            "data": [dict(intervention) for intervention in interventions]
        })
        return jsonify(responseObject), 200


class GetSpecificInterventionAPI(MethodView):
    """
    Get a specific intervention
    """
    @token_required
    @swag_from('../docs/get_specific_intervention.yml')
    def get(self, intervention_id):
        intervention = db_name.get_incident(intervention_id)
        if intervention:
            return jsonify({
                "status": 200,
                "data": [dict(intervention)]
            })

        # this code will run if the red-flag doesn't exist
        return jsonify({
            'error': "The intervention doesn't exist",
            'status': 404
        })


class CreateInterventionsAPI(MethodView):
    """
    Create interventions here
    """
    @token_required
    @swag_from('../docs/add_intervention.yml')
    def post(self):
        """
        add an intervention
        """
        # check for empty request
        if not request.is_json:
            return jsonify({
                'error': 'Request Cannot Be Empty',
                'status': 400
            }), 400

        data = request.get_json()

        # check for missing data in request
        error = None
        if valid_create_data(data):
            error = valid_create_data(data)
        if error:
            return jsonify({"status": 400,
                            "error": error
                            }), 400

        # return if request has no missing data
        incident_id = db_name.create_incident(created_by=data['created_by'], type=data['type'],
                                              location=data['location'], comment=data['comment'],
                                              videos="a.mp4", images="a.jpg")
        return jsonify({"status": 201,
                        "data": [{
                            "id": incident_id,
                            "message": "Created intervention record"
                        }]
                        }), 201


class UpdateStatusAPI(MethodView):
    """
    Patch a redflag status
    """
    @swag_from('../docs/edit_intervention_status.yml')
    @admin_required
    def patch(self, intervention_id):
        # check if request has no json data in its body
        if not request.is_json:
            return jsonify({
                "error": 'Please provide a status',
                "status": 400
            }), 400
        data = request.get_json()

        # check for location in missing data
        error = None
        if wrong_status_data(data):
            error = wrong_status_data(data)

        # validate the data
        if error:
            return jsonify({"status": 400,
                            "error": error
                            }), 400

        # check if record exists
        red_flag = db_name.get_incident(intervention_id)
        if red_flag:
            db_name.edit_incident(intervention_id, 'status', data['status'])
            return jsonify({
                "status": 201,
                "data": [{
                    "id": intervention_id,
                    "message": "Updated intervention record status"
                }]
            }), 201

        # this code will run if the red-flag doesn't exist
        return jsonify({
            "error": 404,
            "message": "Intervention record doesn't exist."
        }), 404


class DeleteInterventionsAPI(MethodView):
    """
    Delete a redflag
    """
    @token_required
    @swag_from('../docs/delete_intervention.yml')
    def delete(self, intervention_id):
        """ This will delete a red-flag specified by id """
        # check if the record exists and delete the record
        red_flag = db_name.get_incident(intervention_id)
        if red_flag:
            db_name.delete_incident(intervention_id, current_identity())
            return jsonify({"status": 200,
                            "data": [{
                                "id": intervention_id,
                                "message": 'intervention record has been deleted'
                            }]
                            }), 200
        # will run if the record doesn't exist
        return jsonify({
            "status": 404,
            "message": "Oops, looks like the record doesn't exist."
        }), 404




# define the API resources
get_interventions_view = GetInterventionsAPI.as_view('get_interventions_api')
get_specific_intervention_view = GetSpecificInterventionAPI.as_view(
    'get_specific_intervention_api')
add_interventions_view = CreateInterventionsAPI.as_view(
    'create_interventions_api')
delete_interventions_view = DeleteInterventionsAPI.as_view(
    'delete_interventions_api')
update_intervention_status = UpdateStatusAPI.as_view('update_status_api')

# add rules for API endpoints
interventions_blueprint.add_url_rule(
    '/interventions',
    view_func=get_interventions_view,
    methods=['GET']
)
interventions_blueprint.add_url_rule(
    '/interventions/<int:intervention_id>',
    view_func=get_specific_intervention_view,
    methods=['GET']
)
interventions_blueprint.add_url_rule(
    '/interventions',
    view_func=add_interventions_view,
    methods=['POST']
)
interventions_blueprint.add_url_rule(
    '/interventions/<int:intervention_id>',
    view_func=delete_interventions_view,
    methods=['DELETE']
)
interventions_blueprint.add_url_rule(
    '/interventions/<int:intervention_id>/status',
    view_func=update_intervention_status,
    methods=['PATCH']
)

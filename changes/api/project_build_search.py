from __future__ import absolute_import, division, unicode_literals

from flask import request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from changes.api.base import APIView
from changes.models import Project, Build


class ProjectBuildSearchAPIView(APIView):
    def _get_project(self, project_id):
        project = Project.query.options(
            joinedload(Project.repository, innerjoin=True),
        ).filter_by(slug=project_id).first()
        if project is None:
            project = Project.query.options(
                joinedload(Project.repository),
            ).get(project_id)
        return project

    def get(self, project_id):
        project = self._get_project(project_id)
        if not project:
            return '', 404

        query = request.args.get('q', request.args.get('query'))
        source = request.args.get('source')

        filters = []

        if source:
            filters.append(Build.target.startswith(source))

        if query:
            filters.append(or_(
                Build.label.contains(query),
                Build.target.startswith(query),
            ))

        queryset = Build.query.options(
            joinedload('project', innerjoin=True),
            joinedload('author'),
            joinedload('source'),
        ).filter(
            Build.project_id == project.id,
            *filters
        ).order_by(Build.date_created.desc())

        return self.paginate(queryset)

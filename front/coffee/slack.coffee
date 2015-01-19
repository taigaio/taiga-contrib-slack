@.taigaContribPlugins = @.taigaContribPlugins or []

slackInfo = {
    slug: "slack"
    name: "Slack"
    type: "admin"
    adminController: "ContribSlackAdmin"
    adminPartial: "contrib/slack/admin.html"
    module: 'taigaContrib.slack'
}

@.taigaContribPlugins.push(slackInfo)

module = angular.module('taigaContrib.slack', [])

debounce = (wait, func) ->
    return _.debounce(func, wait, {leading: true, trailing: false})

initSlackPlugin = ($tgUrls) ->
    $tgUrls.update({
        "slack": "/slack"
    })

class SlackAdmin
    @.$inject = [
        "$rootScope",
        "$scope",
        "$tgModel",
        "$tgRepo",
        "$tgResources"
        "$routeParams",
        "$appTitle"
    ]

    constructor: (@rootScope, @scope, @model, @repo, @rs, @params, @appTitle, @confirm) ->
        @scope.sectionName = "Slack" #i18n
        @scope.project = {}
        @scope.adminPlugins = _.filter(@rootScope.contribPlugins, (plugin) -> plugin.type == "admin")

        promise = @.loadInitialData()

        promise.then () =>
            @appTitle.set("Slack - " + @scope.project.name)

        promise.then null, ->
            @confirm.notify("error")

    loadSlackHooks: ->
        return @repo.queryMany("slack", {project: @scope.projectId}).then (slackhooks) =>
            @scope.slackhook = {project: @scope.projectId}
            if slackhooks.length > 0
                @scope.slackhook = slackhooks[0]

    loadProject: ->
        return @rs.projects.get(@scope.projectId).then (project) =>
            @scope.project = project
            @scope.$emit('project:loaded', project)
            return project

    loadInitialData: ->
        promise = @repo.resolve({pslug: @params.pslug}).then (data) =>
            @scope.projectId = data.project
            return data

        return promise.then(=> @.loadProject())
                      .then(=> @.loadSlackHooks())

module.controller("ContribSlackAdminController", SlackAdmin)

SlackWebhooksDirective = ($repo, $confirm, $loading) ->
    link = ($scope, $el, $attrs) ->
        form = $el.find("form").checksley({"onlyOneErrorElement": true})
        submit = debounce 2000, (event) =>
            event.preventDefault()

            return if not form.validate()

            $loading.start(submitButton)

            if $scope.slackhook.id
                promise = $repo.save($scope.slackhook)
            else
                promise = $repo.create("slack", $scope.slackhook)
            promise.then ->
                $loading.finish(submitButton)
                $confirm.notify("success")

            promise.then null, (data) ->
                $loading.finish(submitButton)
                form.setErrors(data)
                if data._error_message
                    $confirm.notify("error", data._error_message)

        submitButton = $el.find(".submit-button")

        $el.on "submit", "form", submit
        $el.on "click", ".submit-button", submit

    return {link:link}

module.directive("contribSlackWebhooks", ["$tgRepo", "$tgConfirm", "$tgLoading", SlackWebhooksDirective])

module.run(["$tgUrls", initSlackPlugin])

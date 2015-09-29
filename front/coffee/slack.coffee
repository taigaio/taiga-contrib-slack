@.taigaContribPlugins = @.taigaContribPlugins or []

slackInfo = {
    slug: "slack"
    name: "Slack"
    type: "admin"
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
        "$tgRepo",
        "tgAppMetaService",
        "$tgConfirm",
        "$tgHttp",
    ]

    constructor: (@rootScope, @scope, @repo, @appMetaService, @confirm, @http) ->
        @scope.sectionName = "Slack" # i18n
        @scope.sectionSlug = "slack"

        @scope.$on "project:loaded", =>
            promise = @repo.queryMany("slack", {project: @scope.projectId})

            promise.then (slackhooks) =>
                @scope.slackhook = {
                    project: @scope.projectId,
                    notify_userstory_create: true,
                    notify_userstory_change: true,
                    notify_userstory_delete: true,
                    notify_task_create: true,
                    notify_task_change: true,
                    notify_task_delete: true,
                    notify_issue_create: true,
                    notify_issue_change: true,
                    notify_issue_delete: true,
                    notify_wikipage_create: true,
                    notify_wikipage_change: true,
                    notify_wikipage_delete: true
                }
                if slackhooks.length > 0
                    @scope.slackhook = slackhooks[0]

                title = "#{@scope.sectionName} - Plugins - #{@scope.project.name}" # i18n
                description = @scope.project.description
                @appMetaService.setAll(title, description)

            promise.then null, =>
                @confirm.notify("error")

    testHook: () ->
        promise = @http.post(@repo.resolveUrlForModel(@scope.slackhook) + '/test')
        promise.success (_data, _status) =>
            @confirm.notify("success")
        promise.error (data, status) =>
            @confirm.notify("error")

module.controller("ContribSlackAdminController", SlackAdmin)

SlackWebhooksDirective = ($repo, $confirm, $loading) ->
    link = ($scope, $el, $attrs) ->
        form = $el.find("form").checksley({"onlyOneErrorElement": true})
        submit = debounce 2000, (event) =>
            event.preventDefault()

            return if not form.validate()

            currentLoading = $loading()
                .target(submitButton)
                .start()

            if not $scope.slackhook.id
                promise = $repo.create("slack", $scope.slackhook)
                promise.then (data) ->
                    $scope.slackhook = data
            else if $scope.slackhook.url
                promise = $repo.save($scope.slackhook)
                promise.then (data) ->
                    $scope.slackhook = data
            else
                promise = $repo.remove($scope.slackhook)
                promise.then (data) ->
                    $scope.slackhook = {
                        project: $scope.projectId,
                        notify_userstory_create: true,
                        notify_userstory_change: true,
                        notify_userstory_delete: true,
                        notify_task_create: true,
                        notify_task_change: true,
                        notify_task_delete: true,
                        notify_issue_create: true,
                        notify_issue_change: true,
                        notify_issue_delete: true,
                        notify_wikipage_create: true,
                        notify_wikipage_change: true,
                        notify_wikipage_delete: true
                    }

            promise.then (data)->
                currentLoading.finish()
                $confirm.notify("success")

            promise.then null, (data) ->
                currentLoading.finish()
                form.setErrors(data)
                if data._error_message
                    $confirm.notify("error", data._error_message)

        submitButton = $el.find(".submit-button")

        $el.on "submit", "form", submit
        $el.on "click", ".submit-button", submit

    return {link:link}

module.directive("contribSlackWebhooks", ["$tgRepo", "$tgConfirm", "$tgLoading", SlackWebhooksDirective])

module.run(["$tgUrls", initSlackPlugin])

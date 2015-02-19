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
        "$appTitle",
        "$tgConfirm",
        "$tgHttp",
    ]

    constructor: (@rootScope, @scope, @repo, @appTitle, @confirm, @http) ->
        @scope.sectionName = "Slack" #i18n
        @scope.sectionSlug = "slack" #i18n

        @scope.$on "project:loaded", =>
            promise = @repo.queryMany("slack", {project: @scope.projectId})

            promise.then (slackhooks) =>
                @scope.slackhook = {project: @scope.projectId}
                if slackhooks.length > 0
                    @scope.slackhook = slackhooks[0]
                @appTitle.set("Slack - " + @scope.project.name)

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

            $loading.start(submitButton)

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
                    $scope.slackhook = {project: $scope.projectId}

            promise.then (data)->
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

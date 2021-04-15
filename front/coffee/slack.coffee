###
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2021-present Kaleidos Ventures SL
###

debounce = (wait, func) ->
    return _.debounce(func, wait, {leading: true, trailing: false})


class SlackAdmin
    @.$inject = [
        "$rootScope",
        "$scope",
        "$tgRepo",
        "tgAppMetaService",
        "$tgConfirm",
        "$tgHttp",
        "tgProjectService"
    ]

    constructor: (@rootScope, @scope, @repo, @appMetaService, @confirm, @http, @projectService) ->
        @scope.sectionName = "Slack" # i18n
        @scope.sectionSlug = "slack"

        @scope.project = @projectService.project.toJS()
        @scope.projectId = @scope.project.id

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


SlackWebhooksDirective = ($repo, $confirm, $loading, $analytics) ->
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
                    $analytics.trackEvent("slack", "create", "Create slack integration", 1)
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

module = angular.module('taigaContrib.slack', [])

module.controller("ContribSlackAdminController", SlackAdmin)
module.directive("contribSlackWebhooks", ["$tgRepo", "$tgConfirm", "$tgLoading", "$tgAnalytics", SlackWebhooksDirective])

initSlackPlugin = ($tgUrls) ->
    $tgUrls.update({
        "slack": "/slack"
    })
module.run(["$tgUrls", initSlackPlugin])

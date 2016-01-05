describeComponent('mail_view/ui/attachment_list', function () {
    'use strict';

    describe('initialization', function () {
        beforeEach(function () {
            this.setupComponent('<div id="attachment-list">' +
                '<ul id="attachment-list-item"></ul>' +
                '</div>');
        });

        it('should trigger add attachment event', function () {
            var triggerUploadAttachment = spyOnEvent(document, Pixelated.events.mail.appendAttachment);
            var stubAttachment = {attachment_id: 'faked'};

            $(document).trigger(Pixelated.events.mail.uploadedAttachment, stubAttachment);

            expect(triggerUploadAttachment).toHaveBeenTriggeredOnAndWith(document, stubAttachment);
        });

        it('should render attachment list view based on uploadedAttachment event', function () {
            var stubAttachment = {attachment_id: 'faked', filename: 'haha.txt', filesize: 4500};

            $(document).trigger(Pixelated.events.mail.uploadedAttachment, stubAttachment);

            var expected_li = '<li><a href="/attachment/faked?filename=haha.txt&amp;encoding=base64">haha.txt (4.39 Kb)</a></li>';
            expect(this.component.select('attachmentListItem').html()).toEqual(expected_li);
        });

        it('should tear down when email sent', function () {
            var mockTearDown = spyOn(this.Component.prototype, 'resetAll');
            this.setupComponent('<div id="attachment-list">' +
                '<ul id="attachment-list-item"></ul>' +
                '</div>');
            $(document).trigger(Pixelated.events.mail.sent);

            expect(mockTearDown).toHaveBeenCalled();
        });

        xit('should start uploading attachments', function () {
            var stubAttachment = {attachment_id: 'faked', filename: 'haha.txt', filesize: 4500};
            var mockAjax = spyOn($, 'ajax').and.callFake(function (params) {params.success(stubAttachment);});
            var uploadedAttachment = spyOnEvent(document, Pixelated.events.mail.uploadedAttachment);
            var uploading = spyOnEvent(document, Pixelated.events.mail.uploadingAttachment);

            $(document).trigger(Pixelated.events.mail.startUploadAttachment);

            expect(mockAjax).toHaveBeenCalled();
            expect(uploadedAttachment).toHaveBeenTriggeredOnAndWith(document, stubAttachment);
            expect(uploading).toHaveBeenTriggeredOn(document);
        });

    });

});

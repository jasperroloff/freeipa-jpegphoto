// inspired by https://github.com/teicee/freeipa-widget-picture

define(['freeipa/ipa', 'freeipa/phases', 'freeipa/widget', 'freeipa/reg', 'freeipa/text', 'freeipa/user', 'dojo/on', 'exports'], function(IPA, phases, widget, reg, text, user, on, exp) {
    IPA.picture_widget = function (spec) {
        spec = spec || {}

        var that = IPA.input_widget(spec);

        that.accept = spec.accept || "image/*";
        that.height = spec.height || 160;

        that.create = function (container) {
            that.widget_create(container);
            var id = IPA.html_util.get_next_id(that.name);

            // if readonly, display the img only:
            that.display_control = $('<img/>', {
                name: that.name,
                style: `max-height: ${that.height}px`,
                'class': "form-control-static img-thumbnail",
                alt: "avatar"
            }).appendTo(container);

            // if editable, display a div with image & buttons:
            that.input_group = $('<div/>').appendTo(container);

            // file input element
            that.input = $('<input/>', {
                type: "file",
                'class': "hidden",
                accept: that.accept,
                name: that.name,
                id: id
            }).appendTo(that.input_group);

            // btn group
            that.input_group_btn = $('<div/>', {
                'class': 'input-group-btn'
            }).appendTo(that.input_group);

            // btn for setting a picture
            that.input_button = $('<label/>', {
                'class': "btn btn-default",
                'style': "padding-top: 2px;",
                'title': "Load a picture file",
                'text': text.get('@i18n:buttons.set'),
                'for': id
            }).appendTo(that.input_group_btn);

            // btn for removing the current picture
            that.input_remove = $('<button/>', {
                'class': "btn btn-default",
                'title': "Remove current picture",
                'text': text.get('@i18n:buttons.remove'),
            }).appendTo(that.input_group_btn);

            // when the remove button is being clicked, clear the jpegphoto field
            that.input_remove.on('click', function () {
                that.clear();
            });

            // create undo button if wanted
            if (that.undo) {
                that.create_undo(that.input_group_btn);
            }

            that.create_error_link(container);
            that.set_enabled(that.enabled);
            that.update_read_only();

            that.flag_displayed = false;
            that.input.on('change', function () {
                if (!this.files.length) return;
                that.display_control[0].src = URL.createObjectURL(this.files[0]);
                that.display_control.css({opacity: 0.5}).show();
                that.flag_displayed = true;
                var reader = new FileReader();
                reader.addEventListener("load", function () {
                    that.update([this.result.replace(/^data:.*base64,/, '')]);
                }, false);
                reader.readAsDataURL(this.files[0]);
            });
            that.display_control.on('load', function () {
                URL.revokeObjectURL(this.src);
            });
        };

        that.update_read_only = function () {
            if (!that.input) return;
            that.input_group.css('display', that.is_writable() ? '' : 'none');
        };

        /**
         * Convert base64-encoded binary string into a Blob object.
         */
        that.blob_from_base64 = function (b64data) {
            var byteArrays = [];
            var byteCharacters = atob(b64data);
            for (var offset = 0; offset < byteCharacters.length; offset += 512) {
                var slice = byteCharacters.slice(offset, offset + 512);
                var byteNumbers = new Array(slice.length);
                for (var i = 0; i < slice.length; i++) byteNumbers[i] = slice.charCodeAt(i);
                byteArrays.push(new Uint8Array(byteNumbers));
            }
            return new Blob(byteArrays);
        }

        that.update = function (values) {
            if (!values || !values.length) return that.clear();
            if (that.input_debug) that.input_debug.val(values[0]);
            var blob = that.blob_from_base64(values[0]);
            if (blob.size > 100*1024) {
                alert('maximal 100 kB allowed!');
                throw new Error('file is too big');
            }
            that.display_control.css({opacity: 0.5});
            if (!that.flag_displayed) that.display_control[0].src = URL.createObjectURL(blob);
            that.flag_displayed = false;
            that.display_control.data('empty', false).css({opacity: 1.0}).show();
            that.input_remove.show();
            that.on_value_changed(values); // ([ values[0] ]);
        };

        that.save = function () {
            return that.value;
        };

        // clear jpegphoto field
        that.clear = function () {
            that.display_control[0].src = 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='; // 1px GIF
            that.display_control.data('empty', true).hide();
            that.input_remove.hide();
            if (that.input_debug) that.input_debug.val('');
            that.input.val('');
            that.on_value_changed([]);
        };

        return that;
    };

    exp.register = function () {
        reg.widget.register('picture', IPA.picture_widget);
    };

    phases.on('registration', exp.register);

    // helper function
    function get_item(array, attr, value) {
        for (var i = 0, l = array.length; i < l; i++) {
            if (array[i][attr] === value) return array[i];
        }
        return null;
    }

    // Adds 'jpegPhoto' field into user details facet
    user.add_jpegphoto_pre_op = function () {
        var facet = get_item(user.entity_spec.facets, '$type', 'details');
        if (!facet) return;
        var section = get_item(facet.sections, 'name', 'identity');
        if (!section) return;

        section.fields.push({
            name: 'jpegphoto',
            label: "Avatar",
            $type: 'picture',
            accept: 'image/jpeg,image/png',
            height: 240,
        });
        return true;
    };

    phases.on('customization', user.add_jpegphoto_pre_op);

    return exp;
});

//Functions declaration

  function sortableList() {
    console.log('sort changed');
    var formData = {};

    //?TODO formData.ajax_request = "edit_moveact"

    formData.ajax_request = true;
    var liIds = $('#tabslist li').map(function(i, n) {
      return $(n).attr('id');
    }).get().join('&');
    cat_name = $('#select_category').val();
    formData.cat_name = cat_name;
    formData.actions = liIds;
    formData.edit_moveact = 'Move Action';
    //formData.push({ name: 'edit.moveact', value: 'Move Action'});
    $.ajax({
      type: 'POST',
      url: '@@plonetabs-controlpanel',
      data: formData,
      success: function(response) {
            var json = JSON.parse(response);
            console.log('response from server: ');
            console.log(json);

            if (json.status_code === 200) {
                console.log('display success messages');
            }
            else {
                console.log('display error messages');
            }
      }
    });
  }

  function toggleCollapsible(el, collapse) {
    collapse = typeof collapse !== 'undefined' ? collapse : 'default';

    var node = el.parent('.collapseAdvanced');

    if (collapse !== 'default') {
      if (collapse == true) {
          console.log('removeClass expandedBlock; addClass collapsedBlock');
          node.removeClass('expandedBlock');
          node.addClass('collapsedBlock');
      }
      else {
          console.log('removeClass collapsedBlock; addClass expandedBlock');
          node.removeClass('collapsedBlock');
          node.addClass('expandedBlock');
      }
    }
    else {
      if (node.hasClass('collapsedBlock')) {
          console.log('removeClass collapsedBlock; addClass expandedBlock');
          node.removeClass('collapsedBlock');
          node.addClass('expandedBlock');
      }
      else {
          console.log('removeClass expandedBlock; addClass collapsedBlock');
          node.removeClass('expandedBlock');
          node.addClass('collapsedBlock');
      }
    }

  }

  function startupActions() {
    console.log('running basic methods');
    $('.add-controls input').addClass('allowMultiSubmit');
    $('.edit-controls input').addClass('allowMultiSubmit');
    $('.collapseAdvanced').removeClass('expandedBlock').addClass('collapsedBlock');
  }

  $(document).ready(function() {
    console.log('document ready');
    $('#plonetabs_form').addClass('kssTabsActive');
    startupActions();
  });


/*CLIENTS METHODS*/

//titleWrapper
    $('#tabslist .titleWrapper').live('click', function() {
        console.log('#tabslist .titleWrapper clicked');
        ($(this).closest('li')).addClass('editing');
    });

//collapse
    $('.collapseAdvanced .headerAdvanced').live('click', function(event) {
        console.log('.collapseAdvanced .headerAdvanced clicked');
        toggleCollapsible($(this));
    });

/*AJAX METHODS*/

//save(edit)
  $('#tabslist .editsave').live('click', function(event) {
      console.log('.editsave clicked ');
      event.preventDefault();
      var formData = $(this).closest('form').serializeArray();
      formData.push({ name: 'edit_save', value: this.value });

      //?TODO formData.ajax_request = "edit_save"

      formData.push({ name: 'ajax_request', value: true });
      $.ajax({
        type: 'POST',
        url: '@@plonetabs-controlpanel',
        data: formData,
        success: function(response) {
            var json = JSON.parse(response);
            console.log('response from server: ');
            console.log(json);
            if (json.status_code === 200) {
                console.log('display success messages');

                $(this).closest('li').replaceWith(json.content);
            } else {
                console.log('display error messages');

                //if 'id' in errors or 'available_expr' in errors or 'url_expr' in errors:
                toggleCollapsible($(this).find('.headerAdvanced'), false);
            }
        }
    });
  });

//reset(cancel)
  $('#tabslist .editcancel').live('click', function(event) {
      console.log('.editcancel clicked ');
      event.preventDefault();
      var formData = {};
      formData.ajax_request = true;

      //?TODO formData.ajax_request = "edit_cancel"

      formData.edit_cancel = 'Cancel';
      var parentFormSelect = $(this).closest('li');
      formData.orig_id = parentFormSelect.find('.editform input[name="orig_id"]').val();
      formData.category = parentFormSelect.find('.editform input[name="category"]').val();
      $.ajax({
        type: 'POST',
        url: '@@plonetabs-controlpanel',
        data: formData,
        success: function(response) {
            var json = JSON.parse(response);
            console.log('response from server: ');
            console.log(json);

            if (json.status_code === 200) {
                console.log('display success messages');
                parentFormSelect.replaceWith(json.content);

            }
            else {
                console.log('display error messages');
            }
        }

  });
});

//delete
  $('#tabslist .delete').live('click', function(event) {
      console.log('.delete clicked ');
      event.preventDefault();
      var formData = {};
      formData.ajax_request = true;

      //?TODO formData.ajax_request = "edit_delete"

      formData.edit_delete = 'Delete';
      var parentFormSelect = $(this).closest('li');
      formData.orig_id = parentFormSelect.find('.editform input[name="orig_id"]').val();
      formData.category = parentFormSelect.find('.editform input[name="category"]').val();
      $.ajax({
        type: 'POST',
        url: '@@plonetabs-controlpanel',
        data: formData,
        success: function(response) {
            var json = JSON.parse(response);
            console.log('response from server: ');
            console.log(json);
            if (json.status_code === 200) {
                console.log('display success messages');
                parentFormSelect.remove();
            }
            else {
                console.log('display error messages');
            }

        }

  });
});

//visibility
  $('#tabslist input.visibility').live('click', function(event) {
      var formData = {};
      formData.ajax_request = true;
      console.log('#tabslist input.visibility clicked ');
      formData.tabslist_visible = 'Set visibillity';
      var parentFormSelect = $(this).closest('li');
      formData.orig_id = parentFormSelect.find('.editform input[name="orig_id"]').val();
      formData.category = parentFormSelect.find('.editform input[name="category"]').val();
      formData.visibility = $(this).is(':checked');

      $.ajax({
        type: 'POST',
        url: '@@plonetabs-controlpanel',
        data: formData,
        success: function(response) {
            var json = JSON.parse(response);
            console.log('response from server: ');
            console.log(json);


            if (json.status_code === 200) {
                console.log('display success messages');

                if (formData.visibility === true) {
                    parentFormSelect.removeClass('invisible');
                }
                else {
                    parentFormSelect.addClass('invisible');
                }
            }
            else {
                console.log('display error messages');
            }
        }

  });
});

//changing category
  $('#select_category').change(function(event) {
        var formData = {};
        formData.ajax_request = true;
        console.log('select_category changed ');
        formData.category = $(this).val();
        formData.category_change = 'Change';
        $.ajax({
          type: 'POST',
          url: '@@plonetabs-controlpanel',
          data: formData,
          success: function(response) {
              var json = JSON.parse(response);
              console.log(json);
              if (json.status_code === 200) {
                  console.log('display success messages');
                  $('form[name=addaction_form] input[name=category]').text($('#select_category').val());
                  $('#tabslist').html(json.actionslist);
                  $('#autogeneration_section').html(json.section);
                  $('#plonetabs-form-title').text(json.title);

                  $('#addaction').removeClass('adding');
                  toggleCollapsible($('form[name=addaction_form] .headerAdvanced'), true);

                  //Sorting lists
                  $('#tabslist').unbind();
                  $('#tabslist').sortable().bind('sortupdate', function() {sortableList()});

                  //Running startupActions
                  startupActions();
              }
              else {
                  console.log('display error messages');
              }
          }
        });
  });

//portal_tabs methods

//visibility
  $('#roottabs .visibility').live('click', function(event) {
      var formData = {};
      formData.ajax_request = true;
      console.log('#roottabs .visibility clicked ');
      formData.roottabs_visible = 'Visibillity';
      var parentFormSelect = $(this).closest('li');
      formData.orig_id = parentFormSelect.attr('id');
      formData.visibility = $(this).is(':checked');
      $.ajax({
        type: 'POST',
        url: '@@plonetabs-controlpanel',
        data: formData,
        success: function(response) {
            var json = JSON.parse(response);
            console.log('response from server: ');
            console.log(json);
            if (json.status_code === 200) {
                console.log('display success messages');
                $('#portal-globalnav').load(' #portal-globalnav>*');
                if (formData.visibility === true) {
                    parentFormSelect.removeClass('invisible');
                }
                else {
                    parentFormSelect.addClass('invisible');
                }

            }
            else {
                console.log('display error messages');
            }
        }

  });
});

//General func for toggleGeneratedTabs and nonfolderish_tabs request
  function sendRequest(field_name, checked_status) {
    var formData = {};
    formData.ajax_request = true;
    formData.field = field_name;
    formData.generated_tabs = checked_status;
    $.ajax({
      type: 'POST',
      url: '@@plonetabs-controlpanel',
      data: formData,
      success: function(response) {
          var json = JSON.parse(response);
          console.log('response from server: ');
          console.log(json);
          if (json.status_code === 200) {
              $('#roottabs').html(json.content);
              $('#portal-globalnav').load(' #portal-globalnav>*');
              console.log('display success messages');
          }
          else {
              console.log('display error messages');
          }
      }
    });
  }

//toggleGeneratedTabs
  $('#generated_tabs').live('click', function() {
      console.log('#generated_tabs clicked ');
      var field_name = 'disable_folder_sections';
      var checked_status = $(this).is(':checked');
      sendRequest(field_name, checked_status);
  });

//nonfolderish_tabs
  $('#nonfolderish_tabs').live('click', function() {
      console.log('#nonfolderish_tabs clicked ');
      var field_name = 'disable_nonfolderish_sections';
      var checked_status = $(this).is(':checked');
      sendRequest(field_name, checked_status);
  });



//Add new action methods

//focus
    $('#actname').live('focus', function() {
        console.log('#actname on focus');
        $('#addaction').addClass('adding');
    });

//cancel
  $('#buttoncancel').live('click', function(event) {
      console.log('#buttoncancel clicked ');
      event.preventDefault();
      $('#addaction').removeClass('adding');
      toggleCollapsible($('form[name=addaction_form] .headerAdvanced'), true);
      //('#kssPortalMessage').css("display", "none");
  });

//add
  //TODO: add #addaction:submit event processing
  $('#buttonadd').live('click', function(event) {
      console.log('#buttonadd clicked ');
      event.preventDefault();
      var formData = $(this).closest('form').serializeArray();
      formData.push({ name: 'add_add', value: this.value });
      formData.push({ name: 'ajax_request', value: true });
      formData.push({ name: 'cat_name', value: $('#select_category').val() });

      $.ajax({
        type: 'POST',
        url: '@@plonetabs-controlpanel',
        data: formData,
        success: function(response) {
          var json = JSON.parse(response);
          console.log('response from server: ');
          console.log(json);
          if (json.status_code === 200) {
            console.log('display success messages');

            $('#tabslist').append(json.content);
            $('addaction').removeClass('adding');
            toggleCollapsible($('form[name=addaction_form] .headerAdvanced'), true);

            //TODO
            //self.kss_blur(ksscore.getHtmlIdSelector('actname'))

          }
          else {
            console.log('display error messages');

            //TODO
            //if 'id' in errors or 'available_expr' in errors:
            toggleCollapsible($('form[name=addaction_form] .headerAdvanced'), false);


          }
        }
    });
  });

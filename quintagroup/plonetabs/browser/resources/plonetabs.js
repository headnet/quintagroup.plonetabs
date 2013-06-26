//Functions declaration

  function clearStatusMessage() {
    $('#kssPortalMessage').removeClass('info').removeClass('warning').removeClass('error');
  }

  function initStatusMessage(type, header){
    $('#kssPortalMessage').addClass(type);
    $('#kssPortalMessage dt').text(header);
  }

  function setStatusMessage(type, message){
    clearStatusMessage();
    if(type === 'info'){
      initStatusMessage('info', 'Info');
    }
    else if(type === 'error'){
      initStatusMessage('error', 'Error');
    }
    else if(type === 'warning'){
      initStatusMessage('warning', 'Warning');
    }
    $('#kssPortalMessage dd').text(message);
    $('#kssPortalMessage').show()
    //('#kssPortalMessage').show().delay(5000).hide();
  }

  function clearAddForm() {
    $('#addaction').removeClass('adding');
    toggleCollapsible($('form[name=addaction_form] .headerAdvanced'), true);
    $('form[name=addaction_form]')[0].reset();
  }

  function sortableList() {
    var formData = {};
    formData.ajax_request = true;
    var liIds = $('#tabslist li').map(function(i, n) {
      return $(n).attr('id');
    }).get().join('&');
    cat_name = $('#select_category').val();
    formData.cat_name = cat_name;
    formData.actions = liIds;
    formData.edit_moveact = 'Move Action';
    $.ajax({
      type: 'POST',
      url: '@@plonetabs-controlpanel',
      data: formData,
      success: function(response) {
            var json = JSON.parse(response);
            if (json.status_code === 200) {
                setStatusMessage('info', json.status_message);
            }
            else {
                setStatusMessage('error', json.status_message);
            }
      }
    });
  }

  function toggleCollapsible(el, collapse) {
    collapse = typeof collapse !== 'undefined' ? collapse : 'default';

    var node = el.parent('.collapseAdvanced');

    if (collapse !== 'default') {
      if (collapse == true) {
          node.removeClass('expandedBlock');
          node.addClass('collapsedBlock');
      }
      else {
          node.removeClass('collapsedBlock');
          node.addClass('expandedBlock');
      }
    }
    else {
      if (node.hasClass('collapsedBlock')) {
          node.removeClass('collapsedBlock');
          node.addClass('expandedBlock');
      }
      else {
          node.removeClass('expandedBlock');
          node.addClass('collapsedBlock');
      }
    }
  }

  function startupActions() {
    $('.add-controls input').addClass('allowMultiSubmit');
    $('.edit-controls input').addClass('allowMultiSubmit');
    $('.collapseAdvanced').removeClass('expandedBlock').addClass('collapsedBlock');
  }

  $(document).ready(function() {
    $('#plonetabs_form').addClass('kssTabsActive');
    startupActions();
  });


/*CLIENTS METHODS*/

//titleWrapper
    $('#tabslist .titleWrapper').live('click', function() {
        ($(this).closest('li')).addClass('editing');
    });

//collapse
    $('.collapseAdvanced .headerAdvanced').live('click', function(event) {
        toggleCollapsible($(this));
    });

/*AJAX METHODS*/

//save(edit)
  $('#tabslist .editsave').live('click', function(event) {
      event.preventDefault();
      var formData = $(this).closest('form').serializeArray();
      formData.push({ name: 'edit_save', value: this.value });
      formData.push({ name: 'ajax_request', value: true });
      
      $.ajax({
        type: 'POST',
        url: '@@plonetabs-controlpanel',
        data: formData,
        success: function(response) {
            var json = JSON.parse(response);
            if (json.status_code === 200) {
                setStatusMessage('info', json.status_message);
                $(this).closest('li').replaceWith(json.content);
            } else {
                setStatusMessage('error', json.status_message);
                //if 'id' in errors or 'available_expr' in errors or 'url_expr' in errors:
                toggleCollapsible($(this).find('.headerAdvanced'), false);
            }
        }
    });
  });

//reset(cancel)
  $('#tabslist .editcancel').live('click', function(event) {
      event.preventDefault();
      var formData = {};
      formData.ajax_request = true;
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
            if (json.status_code === 200) {
                setStatusMessage('info', json.status_message);
                parentFormSelect.replaceWith(json.content);
            }
            else {
                setStatusMessage('error', json.status_message);
            }
        }
  });
});

//delete
  $('#tabslist .delete').live('click', function(event) {
      event.preventDefault();
      var formData = {};
      formData.ajax_request = true;
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
            if (json.status_code === 200) {
                setStatusMessage('info', json.status_message);
                parentFormSelect.remove();
            }
            else {
                setStatusMessage('error', json.status_message);
            }

        }
  });
});

//visibility
  $('#tabslist input.visibility').live('click', function(event) {
      var formData = {};
      formData.ajax_request = true;
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
            if (json.status_code === 200) {
                setStatusMessage('info', json.status_message);
                if (formData.visibility === true) {
                    parentFormSelect.removeClass('invisible');
                }
                else {
                    parentFormSelect.addClass('invisible');
                }
            }
            else {
                setStatusMessage('error', json.status_message);
            }
        }
  });
});

//changing category
  $('#select_category').change(function(event) {
        var formData = {};
        formData.ajax_request = true;
        formData.category = $(this).val();
        formData.category_change = 'Change';
        $.ajax({
          type: 'POST',
          url: '@@plonetabs-controlpanel',
          data: formData,
          success: function(response) {
              var json = JSON.parse(response);
              if (json.status_code === 200) {
                  //display success message
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
                  //display error message
              }
          }
        });
  });

//portal_tabs methods

//visibility
  $('#roottabs .visibility').live('click', function(event) {
      var formData = {};
      formData.ajax_request = true;
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
            if (json.status_code === 200) {
                setStatusMessage('info', json.status_message);
                $('#portal-globalnav').load(' #portal-globalnav>*');
                if (formData.visibility === true) {
                    parentFormSelect.removeClass('invisible');
                }
                else {
                    parentFormSelect.addClass('invisible');
                }

            }
            else {
                setStatusMessage('error', json.status_message);
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
          if (json.status_code === 200) {
              setStatusMessage('info', json.status_message);
              $('#roottabs').html(json.content);
              $('#portal-globalnav').load(' #portal-globalnav>*');
          }
          else {
              setStatusMessage('error', json.status_message);
          }
      }
    });
  }

//toggleGeneratedTabs
  $('#generated_tabs').live('click', function() {
      var field_name = 'disable_folder_sections';
      var checked_status = $(this).is(':checked');
      sendRequest(field_name, checked_status);
  });

//nonfolderish_tabs
  $('#nonfolderish_tabs').live('click', function() {
      var field_name = 'disable_nonfolderish_sections';
      var checked_status = $(this).is(':checked');
      sendRequest(field_name, checked_status);
  });

//Add new action methods

//focus
    $('#actname').live('focus', function() {
        $('#addaction').addClass('adding');
    });

//cancel
  $('#buttoncancel').live('click', function(event) {
      event.preventDefault();
      clearAddForm();
  });

//add
  //TODO: add #addaction:submit event processing
  $('#buttonadd').live('click', function(event) {
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
          if (json.status_code === 200) {
            setStatusMessage('info', json.status_message);
            $('#tabslist').append(json.content);
            clearAddForm();
          }
          else {
            setStatusMessage('error', json.status_message);
            toggleCollapsible($('form[name=addaction_form] .headerAdvanced'), false);
            if (json.content){
              if (json.content.id){
                $('form[name=addaction_form] .field-id .error-container').text(json.content.id);
              }
              if (json.content.title){
                $('form[name=addaction_form] .field-name .error-container').text(json.content.title);
              }
            }
          }
        }
    });
  });

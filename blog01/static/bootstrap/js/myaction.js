/**
 * Created by mona on 2017/9/5.
 */


//**************************login html ******************************************************
//ajax 发送登录验证信息
$('.login_button').click(function () {
    data = {};
    data["csrfmiddlewaretoken"]=$("[name='csrfmiddlewaretoken']").val();
    data[$('#username').attr('name')]=$('#username').val();
    data[$('#password').attr('name')]=$('#password').val();
    data[$('#valid_code').attr('name')]=$('#valid_code').val();

    $.ajax({
            url:'/login/',
            type:'POST',
            data:data,
            success:function (data) {
                data = JSON.parse(data);
                if(data['state']==false){
                    $('.login_error_message').text(data['error_message'])
                }
                else {
                    var path = window.location.pathname;
                    var new_path = path.replace('/login/','/');
                    location.href=new_path;
                }
            }
        })
});


//验证码刷新
$('.img_refresh').click(function () {
    $('.valid_img')[0].src += '?';

});

//****************************register html ***************************************************


//失入焦点时判断密码是否一致
$('#id_re_password').blur(function () {
    var pwd = $('#password').val();
    var re_pwd = $(this).val();
    if (pwd != re_pwd){
       var error_message = '密码不一致';
        $('.password_error_message').text(error_message)
    }
});


//得到焦点时清空错误提示信息
$('#id_re_password').focus(function () {
    $('.password_error_message').text(' ')
});

//ajax 发送注册数据
$('.register_button').click(function () {

    var formData = new FormData();


    var csrfmiddlewaretoken = $("[name='csrfmiddlewaretoken']").val();
    var username = $('#id_username').val();
    var password = $('#id_password').val();
    var re_password = $('#id_re_password').val();
    var email = $('#id_email').val();
    var valid_code = $('#id_valid_code').val();
    var avatar = $('#avatar')[0].files[0];


    formData.append("csrfmiddlewaretoken",csrfmiddlewaretoken);
    formData.append('username',username);
    formData.append('password',password);
    formData.append('re_password',re_password);
    formData.append('email',email);
    formData.append('valid_code', valid_code);
    formData.append('avatar',avatar);

    $.ajax({
            url:'/register/',
            type:'POST',
            data:formData,  //使用formadate，必须设置contentType，processDate为false
            contentType:false,
            processData:false,
            success:function (data) {
                data = JSON.parse(data);
                if (data['state']){
                    location.href = '/login/'
                }
                else {

                    $('.user_error').text(data['error_message']['username']);
                    $('.password_error').text(data['error_message']['password']);
                    $('.email_error').text(data['error_message']['email']);
                    $('.valid_code_error').text(data['error_message']['valid_code']);
                    if (data['error_message']['re_password']) {
                        $('.re_password_error').text(data['error_message']['re_password']);
                    }
                    else {
                        $('.re_password_error').text(data['error_message']['__all__']);
                    }
                }

            }
        })
});


//头像预览

$('.register_avatar_input').change(function () {
    var reader = new FileReader();
    var file = $('.register_avatar_input')[0].files[0];
    reader.readAsDataURL(file);
    reader.onload=function () {
        $('.register_avatar_img')[0].src = this.result;
        console.log($('.register_avatar_img')[0])
    }

});


//***********************************user.html*************************************************************


 //判断当前年份是否是闰年(闰年2月份有29天，平年2月份只有28天)


function loadBlogCalendar(n) {
    $.ajax({
        url: "/mvc/blog/calendar.aspx",
        data: {blogApp: currentBlogApp, dateStr: n},
        type: "get",
        dataType: "text",
        success: function (n) {
            n && ($("#blog-calendar").html(n), $("#blog-calendar").show())
        }
    })
}

// function loadBlogDefaultCalendar() {
//     if ($("#blog-calendar").length) {
//         var t = "", i = $("#cb_post_title_url").attr("href"), n;
//         (n = /\/archive\/(\d{4}\/\d{2}\/\d{2})\//g.exec(i)) ? t = n[1] : (n = /\/archive\/(\d{4}\/\d{2}\/\d{2})\./g.exec(i)) ? t = n[1] : (n = /\/archive\/(\d{4}\/\d{2})./g.exec(i)) && (t = n[1]);
//         loadBlogCalendar(t)
//     }
// }



//***********************************user manage.html*************************************************************

$('.manage_delete').click(function () {
    var current_delete = $(this);
    alert(123);
     var article_id = $(this).next().attr('class');
     var csrfmiddlewaretoken = $("[name='csrfmiddlewaretoken']").val()
     $.ajax({
         url: "/blog/article/delete",
        data: {'csrfmiddlewaretoken':csrfmiddlewaretoken,
             'article_id':article_id},
        type: "POST",

        success: function () {
             current_delete.parent().parent().empty();

        }

     })


});





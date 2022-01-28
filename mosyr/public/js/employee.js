frappe.ui.form.on('Employee', {
	 refresh: function(frm) {
			frm.add_custom_button(__('Identity'), function(){
				window.scrollTo({
					top: 2000,
					left: 2000,
					behavior: 'smooth'

					(this).attr('data-fieldname')

				  });
				  frm.set_df_property('identity', 'reqd', 0);
				
			}, __('ide & pas & stat'));
			frm.add_custom_button(__('Passport'), function(){
				
				
			}, __('ide & pas & stat'));
			frm.add_custom_button(__('Status'), function(){

				
			}, __('ide & pas & stat'));
			frm.add_custom_button(__('Qualification'), function(){

				
			}, __('qua & Exp & con'));
			frm.add_custom_button(__('Experince'), function(){

				
			}, __('qua & Exp & con'));
			frm.add_custom_button(__('Contact'), function(){

				
			}, __('qua & Exp & con'));
			frm.add_custom_button(__('Dependent'), function(){

				
			}, __('dep & ins & sal & leav'));
			frm.add_custom_button(__('Insurance'), function(){

				
			}, __('dep & ins & sal & leav'));
			frm.add_custom_button(__('Salary'), function(){

				
			}, __('dep & ins & sal & leav'));
			frm.add_custom_button(__('Leave'), function(){

				
			}, __('dep & ins & sal & leav'));
	 }

	
});
